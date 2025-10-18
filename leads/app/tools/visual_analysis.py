import base64

from langchain.tools import tool
from loguru import logger
from playwright.sync_api import sync_playwright, Error as PlaywrightError

from app.schemas import VisualAnalysisOutput, CapturedScreenshot, VisualAnalysisInput


# --- Custom Exceptions ---

class ScreenshotCaptureError(Exception):
    """Custom exception raised for errors encountered during website screenshot capture."""
    pass


class WebsiteScreenshotter:
    """
    A class responsible for capturing website screenshots using Playwright.

    This class encapsulates the logic for browser automation via Playwright
    to capture screenshots of a webpage at different resolutions.
    """

    def run(self, url: str) -> VisualAnalysisOutput:
        """
        Executes the screenshot capture workflow.

        Args:
            url (str): The URL of the website to be captured.

        Returns:
            VisualAnalysisOutput: An object containing a list of screenshot data.

        Raises:
            ValueError: If the provided URL is empty or None.
            ScreenshotCapture-CaptureError: If screenshots cannot be captured.
        """
        logger.info(f"Starting screenshot capture workflow for URL: {url}")
        if not url:
            logger.error("Validation failed: URL is empty or None.")
            raise ValueError("Error: A valid URL must be provided.")

        # This method will raise an exception on failure
        return self._capture_screenshots(url)

    @staticmethod
    def _capture_screenshots(url: str) -> VisualAnalysisOutput:
        """
        Captures screenshots of the given URL at various standard screen resolutions using Playwright.

        It uses a headless Chromium browser to navigate to the page and take screenshots
        for desktop, tablet, and mobile viewports.

        Args:
            url (str): The URL of the website to capture.

        Returns:
            VisualAnalysisOutput: An object containing the list of captured screenshots.

        Raises:
            ScreenshotCaptureError: If Playwright fails to initialize the browser or
                                    capture screenshots for any reason.
        """
        resolutions = {
            "desktop": {"width": 1920, "height": 1080},
            "tablet": {"width": 768, "height": 1024},
            "mobile": {"width": 375, "height": 812}
        }
        screenshots = []

        try:
            with sync_playwright() as p:
                logger.info("Initializing Playwright and launching headless Chromium browser...")
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                logger.info("Browser launched successfully.")

                for device, dims in resolutions.items():
                    logger.info(f"Capturing for {device} view ({dims['width']}x{dims['height']})...")
                    page.set_viewport_size(dims)
                    logger.debug(f"Navigating to {url}...")
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)

                    png_screenshot = page.screenshot(full_page=False, type="png")
                    base64_image = f"data:image/png;base64,{base64.b64encode(png_screenshot).decode('utf-8')}"

                    screenshots.append(CapturedScreenshot(
                        device=device,
                        image=base64_image
                    ))
                    logger.info(f"Successfully captured screenshot for {device}.")

                logger.info("Closing browser...")
                browser.close()

        except PlaywrightError as e:
            error_message = f"A Playwright error occurred during screenshot capture: {e}"
            logger.error(error_message, exc_info=True)
            raise ScreenshotCaptureError(error_message) from e
        except Exception as e:
            error_message = f"An unexpected error occurred during screenshot capture: {e}"
            logger.error(error_message, exc_info=True)
            raise ScreenshotCaptureError(error_message) from e

        logger.info(f"Completed screenshot capture. Total screenshots: {len(screenshots)}.")
        return VisualAnalysisOutput(screenshots)


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
        logger.success(f"\n--- Successfully captured screenshots ---")
        for item in data.root:
            logger.success(item.model_dump_json(indent=2))
    else:
        logger.error(f"\n--- Tool returned an error ---")
        logger.error(data.model_dump_json(indent=2))
