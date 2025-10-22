from pydantic import BaseModel, Field


class PageScreenshotterInput(BaseModel):
    urls: list[str] = Field(..., description="List of URLs of the website to screenshot.")


class PageScreenshotData(BaseModel):
    url: str = Field(..., description="URL of the page.")
    screenshot: str = Field(..., description="Base64-encoded screenshot image of the page.")


class PageScreenshotterOutput(BaseModel):
    pages: list[PageScreenshotData] = Field(..., description="List of pages with screenshots.")
