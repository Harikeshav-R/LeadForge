from pydantic import BaseModel, Field


class VisualAnalysisInput(BaseModel):
    url: str = Field(..., description="URL of the website to analyze.")


class PageScreenshotData(BaseModel):
    url: str = Field(..., description="URL of the page.")
    screenshot: str = Field(..., description="Base64-encoded screenshot image of the page.")


class VisualAnalysisOutput(BaseModel):
    pages: list[PageScreenshotData] = Field(..., description="List of pages with screenshots.")
