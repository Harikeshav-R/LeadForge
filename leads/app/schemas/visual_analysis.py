from pydantic import BaseModel, Field, RootModel


class VisualAnalysisInput(BaseModel):
    url: str = Field(..., description="URL of the website to analyze.")


class CapturedScreenshot(BaseModel):
    device: str = Field(..., description="Device type (desktop, tablet, mobile).")
    image: str = Field(..., description="Base64-encoded screenshot image.")


VisualAnalysisOutput = RootModel[list[CapturedScreenshot]]
