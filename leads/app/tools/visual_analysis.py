import base64

from langchain.tools import tool
from playwright.sync_api import sync_playwright, Error as PlaywrightError

from app.schemas.visual_analysis import VisualAnalysisOutput, CapturedScreenshot, VisualAnalysisInput


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
            VisualAnalysisOutput: A list of dictionaries containing screenshot data.

        Raises:
            ValueError: If the provided URL is empty or None.
            ScreenshotCaptureError: If screenshots cannot be captured.
        """
        if not url:
            # Raise a specific error for invalid input
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
            VisualAnalysisOutput: A list of dictionaries, where each dictionary
                                  contains the device type ('desktop', 'tablet',
                                  'mobile') and the base64-encoded JPEG image.

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
                # Launch a headless Chromium browser. Playwright handles the binary installation.
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )

                for device, dims in resolutions.items():
                    page.set_viewport_size(dims)
                    # Use 'domcontentloaded' for faster navigation, as we don't need all assets.
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    # Capture only the viewport, not the full page
                    png_screenshot = page.screenshot(full_page=False, type="png")
                    base64_image = f"data:image/png;base64,{base64.b64encode(png_screenshot).decode('utf-8')}"

                    screenshots.append(CapturedScreenshot(
                        device=device,
                        image=base64_image
                    ))

                browser.close()

        except PlaywrightError as e:
            error_message = f"An error occurred during screenshot capture with Playwright: {e}"
            print(error_message)
            raise ScreenshotCaptureError(error_message) from e
        except Exception as e:
            error_message = f"An unexpected error occurred during screenshot capture: {e}"
            print(error_message)
            raise ScreenshotCaptureError(error_message) from e

        return VisualAnalysisOutput(screenshots)


@tool(args_schema=VisualAnalysisInput)
def website_screenshotter(url: str) -> VisualAnalysisOutput | str:
    """
    Captures screenshots of a website at desktop, tablet, and mobile resolutions
    and returns a list of base64-encoded images.

    Use this tool when you need to get visual data from a webpage.
    The output of this tool is data, not a human-readable analysis.
    """
    try:
        screenshotter = WebsiteScreenshotter()
        return screenshotter.run(url)
    except (ValueError, ScreenshotCaptureError) as e:
        # Return the error message as a string for the agent to process.
        return f"Tool Error: {e}"
    except Exception as e:
        return f"An unexpected tool error occurred: {e}"


# --- Example Usage ---
if __name__ == '__main__':
    print("--- Running Website Screenshotter Tool ---")
    test_url = "https://www.google.com"
    print(f"Capturing URL: {test_url}")
    data = website_screenshotter.run(test_url)

    if isinstance(data, VisualAnalysisOutput):
        print(f"\n--- Successfully captured screenshots ---")
        for item in data.root:
            print(f"Device: {item.device}, Image (first 50 chars): {item.image[:50]}...")
    else:
        print(f"\n--- Tool returned an error ---")
        print(data)
