import asyncio
import base64
from typing import Optional

from langchain.tools import tool
from loguru import logger
from playwright.async_api import async_playwright, Error as PlaywrightError, Browser

from app.schemas import VisualAnalysisOutput, CapturedScreenshot, VisualAnalysisInput


# --- Custom Exceptions ---

class ScreenshotCaptureError(Exception):
    """Custom exception raised for errors encountered during website screenshot capture."""
    pass


class WebsiteScreenshotter:
    """
    A class responsible for capturing website screenshots in parallel using Playwright.
    """

    # Define resolutions and user agent at the class level
    RESOLUTIONS = {
        "desktop": {"width": 1920, "height": 1080},
        "tablet": {"width": 768, "height": 1024},
        "mobile": {"width": 375, "height": 812}
    }
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def run(self, url: str) -> VisualAnalysisOutput:
        """
        Executes the screenshot capture workflow.

        This synchronous method acts as the entry point and runs the
        asynchronous capture logic.
        """
        logger.info(f"Starting screenshot capture workflow for URL: {url}")
        if not url:
            logger.error("Validation failed: URL is empty or None.")
            raise ValueError("Error: A valid URL must be provided.")

        try:
            return asyncio.run(self._capture_screenshots_async(url))
        except Exception as e:
            logger.error(f"Async capture failed: {e}")
            raise ScreenshotCaptureError(f"Failed to run async capture: {e}") from e

    async def _capture_one_viewport_async(
            self,
            browser: Browser,
            url: str,
            device: str,
            dims: dict[str, int]
    ) -> Optional[CapturedScreenshot]:
        """
        Asynchronously captures a single screenshot for a specific viewport.

        This helper runs in its own browser context for parallel isolation.
        """
        context = None
        page = None
        task_name = f"{device} ({dims['width']}x{dims['height']})"
        logger.info(f"[{task_name}] Task starting for {url}.")

        try:
            # Create an isolated context and page for this task
            context = await browser.new_context(
                viewport={"width": dims['width'], "height": dims['height']},
                user_agent=self.USER_AGENT
            )
            page = await context.new_page()

            logger.debug(f"[{task_name}] Navigating...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(1000)  # User's original delay

            logger.info(f"[{task_name}] Capturing screenshot...")
            png_screenshot = await page.screenshot(full_page=False, type="png")
            base64_image = f"data:image/png;base64,{base64.b64encode(png_screenshot).decode('utf-8')}"

            logger.info(f"[{task_name}] Successfully captured screenshot.")
            return CapturedScreenshot(
                device=device,
                image=base64_image
            )

        except PlaywrightError as e:
            logger.error(f"[{task_name}] FAILED. Playwright error: {e}")
            return None  # Return None on failure, don't stop other tasks
        except Exception as e:
            logger.error(f"[{task_name}] FAILED. Unexpected error: {e}", exc_info=True)
            return None  # Return None on failure
        finally:
            # Crucial: clean up this task's resources
            if page:
                await page.close()
            if context:
                await context.close()
            logger.debug(f"[{task_name}] Context/Page closed.")

    async def _capture_screenshots_async(self, url: str) -> VisualAnalysisOutput:
        """
        Runs all viewport screenshot captures in parallel.
        """
        browser = None
        try:
            async with async_playwright() as p:
                logger.info("Initializing Playwright and launching headless Chromium browser...")
                browser = await p.chromium.launch(headless=True)
                logger.info("Browser launched. Creating parallel tasks...")

                # Create a list of tasks to be run concurrently
                tasks = [
                    self._capture_one_viewport_async(browser, url, device, dims)
                    for device, dims in self.RESOLUTIONS.items()
                ]

                # Run all tasks in parallel and wait for them all to complete
                results = await asyncio.gather(*tasks)

                # Filter out None results (from failed tasks)
                successful_screenshots: list[CapturedScreenshot] = [
                    res for res in results if res is not None
                ]

                logger.info(
                    f"All tasks complete. Success: {len(successful_screenshots)}, Failed: {len(self.RESOLUTIONS) - len(successful_screenshots)}")

                if not successful_screenshots:
                    raise ScreenshotCaptureError(f"Failed to capture any screenshots for {url}. Check logs.")

                return VisualAnalysisOutput(successful_screenshots)

        except PlaywrightError as e:
            # This catches browser-level errors (e.g., launch failure)
            error_message = f"A Playwright error occurred during browser setup: {e}"
            logger.error(error_message, exc_info=True)
            raise ScreenshotCaptureError(error_message) from e
        except Exception as e:
            # Catches other unexpected errors during setup
            error_message = f"An unexpected error occurred during screenshot gathering: {e}"
            logger.error(error_message, exc_info=True)
            raise ScreenshotCaptureError(error_message) from e
        finally:
            if browser:
                await browser.close()
                logger.info("Browser closed.")


@tool(args_schema=VisualAnalysisInput)
def visual_analysis(url: str) -> VisualAnalysisOutput | str:
    """
    Captures screenshots of a website at desktop, tablet, and mobile resolutions
    and returns a list of base64-encoded images.

    Use this tool when you need to get visual data from a webpage.
    The output of this tool is data, not a human-readable analysis.
    """
    logger.info(f"Executing website_screenshotter tool for URL: {url}")
    try:
        screenshotter = WebsiteScreenshotter()
        result = screenshotter.run(url)
        logger.info("Tool execution completed successfully.")
        return result
    except (ValueError, ScreenshotCaptureError) as e:
        logger.warning(f"Tool execution failed with a known error: {e}")
        return f"Tool Error: {e}"
    except Exception as e:
        logger.error(f"Tool execution failed with an unexpected error: {e}", exc_info=True)
        return f"An unexpected tool error occurred: {e}"


# --- Example Usage ---
if __name__ == '__main__':
    logger.info("--- Running Website Screenshotter Tool ---")
    test_url = "https://www.google.com"
    logger.info(f"Capturing URL: {test_url}")
    data = visual_analysis.run(test_url)

    if isinstance(data, VisualAnalysisOutput):
        logger.success(f"\n--- Successfully captured {len(data.root)} screenshots ---")
        for item in data.root:
            logger.success(f"Device: {item.device}, Image: {item.image[:60]}...")

    else:
        logger.error(f"\n--- Tool returned an error ---")
        logger.error(data)
