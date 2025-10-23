import asyncio
import base64
from typing import Optional

from langchain_core.tools import tool
from loguru import logger
from playwright.async_api import async_playwright, Browser, Error as PlaywrightError

from app.schemas import PageScreenshotterOutput, PageScreenshotterInput
from app.schemas.page_screenshotter import PageScreenshotData


class PageScreenshotter:
    """
    A class to take screenshots of a list of URLs in parallel using Playwright
    with robust error handling and logging.
    """

    def __init__(self, urls: list[str]):
        """
        Initializes the screenshotter with a list of URLs.

        Args:
            urls: A list of URL strings.
        """
        self.urls = urls
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    async def _take_screenshot(self, url: str, browser: Browser) -> Optional[PageScreenshotData]:
        """
        Internal method to capture a screenshot for a single URL.

        Returns a PageScreenshotData model on success, or None on failure.
        """
        context = None
        page = None
        logger.info(f"[Task {url}] Starting.")

        try:
            # 1. Create a new isolated browser context
            logger.debug(f"[Task {url}] Creating new browser context.")
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()

            # 2. Navigate to the URL
            logger.info(f"[Task {url}] Navigating...")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            logger.info(f"[Task {url}] Navigation successful.")

            # 3. Take the screenshot
            logger.info(f"[Task {url}] Taking screenshot.")
            screenshot_bytes = await page.screenshot(type="png", full_page=True)
            logger.info(f"[Task {url}] Screenshot captured.")

            # 4. Encode and package the data
            base64_string = f"data:image/png;base64,{base64.b64encode(screenshot_bytes).decode('utf-8')}"

            logger.info(f"[Task {url}] Task complete.")
            return PageScreenshotData(url=url, screenshot=base64_string)

        except PlaywrightError as e:
            # Handle specific Playwright errors (e.g., TimeoutError, navigation errors)
            logger.error(f"[Task {url}] FAILED. Playwright error: {e}")
            return None
        except Exception as e:
            # Handle any other unexpected errors
            logger.error(f"[Task {url}] FAILED. Unexpected error: {e}", exc_info=True)
            return None

        finally:
            # 5. Cleanup: Ensure resources are always closed
            if page:
                await page.close()
                logger.debug(f"[Task {url}] Page closed.")
            if context:
                await context.close()
                logger.debug(f"[Task {url}] Context closed.")

    async def run(self) -> list[Optional[PageScreenshotData]]:
        """
        Runs the parallel screenshot process for all URLs.
        """
        logger.info("Launching headless browser...")
        async with async_playwright() as p:
            browser = None
            try:
                browser = await p.chromium.launch(headless=True)
                logger.info("Browser launched. Creating screenshot tasks...")

                tasks = [self._take_screenshot(url, browser) for url in self.urls]

                logger.info(f"Running {len(tasks)} screenshot tasks in parallel...")
                results = await asyncio.gather(*tasks)
                logger.info("All tasks completed.")

                return results

            except Exception as e:
                logger.critical(f"A critical error occurred during the main run: {e}", exc_info=True)
                # If the browser launch fails, all tasks will fail
                return [None] * len(self.urls)
            finally:
                if browser:
                    await browser.close()
                    logger.info("Browser closed.")


# --- Global Wrapper Function ---
@tool(args_schema=PageScreenshotterInput)
def page_screenshotter(urls: list[str]) -> PageScreenshotterOutput:
    """
    A global wrapper function that instantiates and runs the PageScreenshotter.

    Args:
        urls: A list of URL strings.

    Returns:
        A PageScreenshotterOutput object containing a list of
        successful PageScreenshotData.
    """
    logger.info(f"Received request to screenshot {len(urls)} URLs.")
    if not urls:
        logger.warning("No URLs provided, returning empty list.")
        return PageScreenshotterOutput([])

    screenshotter = PageScreenshotter(urls)

    # Run the main async function
    results = asyncio.run(screenshotter.run())

    # Filter out the None (failed) results
    successful_pages: list[PageScreenshotData] = [
        page_data for page_data in results if page_data is not None
    ]

    failed_count = len(urls) - len(successful_pages)
    logger.success(f"Screenshot process finished. Success: {len(successful_pages)}, Failed: {failed_count}")

    # Return the final Pydantic model
    return PageScreenshotterOutput(successful_pages)


if __name__ == "__main__":
    example_urls = [
        "https://www.google.com",
        "https://github.com",
        "https://www.python.org",
        "https://this-is-not-a-real-domain.invalid",
        "https://bing.com",
        "https://stackoverflow.com/404"
    ]

    logger.info("--- Starting Screenshot Tool ---")

    screenshot_output: PageScreenshotterOutput = page_screenshotter.invoke(
        PageScreenshotterInput(urls=example_urls).model_dump())

    logger.success("\n--- Tool Output (Successful) ---")

    # The output is a Pydantic model
    if screenshot_output.root:
        # Print summary
        for page in screenshot_output.root:
            logger.success(f"  URL: {page.url}")
            logger.success(f"  Screenshot (Base64): {page.screenshot[:70]}...")
            logger.success("  " + "-" * 20)

    else:
        logger.error("No screenshots were captured successfully.")
