from loguru import logger

from app.schemas import State, PageScreenshotterInput, PageScreenshotterOutput
from app.tools import page_screenshotter


def page_screenshotter_node(state: State) -> State:
    """
    Takes screenshots of all URLs found in the `pages_scraped` list.

    This function extracts URLs from the state, invokes the
    `page_screenshotter` tool, and updates the state with either
    the list of screenshots or an error message if it fails.

    Args:
        state: The current workflow state, containing `pages_scraped`.

    Returns:
        State: An updated copy of the state. If successful, `pages_screenshots`
               is populated and `screenshot_error` is None. If failed,
               `pages_screenshots` is empty and `screenshot_error` contains
               the error message.
    """
    logger.info(f"Starting page screenshot process for {len(state.pages_scraped)} pages.")

    if not state.pages_scraped:
        logger.warning("No scraped pages found in state. Skipping screenshot node.")
        return state.model_copy(
            update={
                "pages_screenshots": [],
            }
        )

    try:
        # 1. Prepare the input for the screenshotter
        website_urls = [page.url for page in state.pages_scraped]
        input_data = PageScreenshotterInput(
            urls=website_urls,
        ).model_dump()

        logger.debug(f"Invoking page_screenshotter for URLs: {website_urls}")

        # 2. Invoke the screenshotter
        screenshot_information: PageScreenshotterOutput = page_screenshotter.invoke(input_data)

        screenshot_count = len(screenshot_information.root)
        logger.info(f"Successfully captured {screenshot_count} screenshots.")

        # 3. Return the new state on success
        return state.model_copy(
            update={
                "pages_screenshots": screenshot_information.root,
            }
        )

    except Exception as e:
        # 4. Handle any exception during the screenshotting process
        error_message = f"Failed to take screenshots: {e}"
        logger.error(error_message, exc_info=True)  # exc_info=True logs the stack trace

        # 5. Return the new state on failure
        return state.model_copy(
            update={
                "pages_screenshots": [],  # Ensure screenshots list is empty on failure
            }
        )
