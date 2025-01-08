import json
import time
from typing import List, Optional, Tuple, Dict

from autogen import AssistantAgent, register_function

from ...markdown_browser import RequestsMarkdownBrowser
from ..base_worker import BaseWorker

# from typing_extensions import Annotated
from ._tools import TOOL_FIND_NEXT, TOOL_FIND_ON_PAGE_CTRL_F, TOOL_OPEN_LOCAL_FILE, TOOL_PAGE_DOWN, TOOL_PAGE_UP


@default_subscription
class FileSurfer(AssistantAgent):
    """An agent that uses tools to read and navigate local files."""

    DEFAULT_DESCRIPTION = "An agent that can handle local files."

    DEFAULT_SYSTEM_MESSAGE = """
        You are a helpful AI Assistant.
        When given a user query, use available functions to help the user with their request."""

    def __init__(
        self,
        llm_config: Dict,
        description: str = DEFAULT_DESCRIPTION,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        browser: Optional[RequestsMarkdownBrowser] = None,
    ) -> None:
        super().__init__("filesurfer", llm_config=llm_config,
                         system_message=system_message,
                         description=description)
        # self._tools = [TOOL_OPEN_LOCAL_FILE, TOOL_PAGE_UP, TOOL_PAGE_DOWN, TOOL_FIND_ON_PAGE_CTRL_F, TOOL_FIND_NEXT]

    def _get_browser_state(self) -> Tuple[str, str]:
        """
        Get the current state of the browser, including the header and content.
        """
        if self._browser is None:
            self._browser = RequestsMarkdownBrowser(viewport_size=1024 * 5, downloads_folder="coding")

        header = f"Address: {self._browser.address}\n"

        if self._browser.page_title is not None:
            header += f"Title: {self._browser.page_title}\n"

        current_page = self._browser.viewport_current_page
        total_pages = len(self._browser.viewport_pages)

        address = self._browser.address
        for i in range(len(self._browser.history) - 2, -1, -1):  # Start from the second last
            if self._browser.history[i][0] == address:
                header += f"You previously visited this page {round(time.time() - self._browser.history[i][1])} seconds ago.\n"
                break

        header += f"Viewport position: Showing page {current_page+1} of {total_pages}.\n"

        return (header, self._browser.viewport)
