import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas import PageScrapedData
from app.schemas.page_screenshotter import PageScreenshotData


class StateBase(BaseModel):
    initial_website_url: str = Field(..., description="The URL of the initial website to scrape and recreate.")
    prompt: str | None = Field(None, description="The prompt to generate the website from.")
    pages_scraped: list[PageScrapedData] = Field(default_factory=list,
                                                 description="Scraped pages from the initial website.")
    pages_screenshots: list[PageScreenshotData] = Field(default_factory=list,
                                                        description="Screenshotted pages from the initial website.")
    final_website_zip: bytes | None = Field(None, description="Final production website zip file.")


class StateCreate(StateBase):
    pass


class StateUpdate(BaseModel):
    initial_website_url: Optional[str] = Field(None,
                                               description="The URL of the initial website to scrape and recreate.")
    prompt: Optional[str] = Field(None, description="The prompt to generate the website from.")
    pages_scraped: Optional[list[PageScrapedData]] = Field(default_factory=list,
                                                           description="Scraped pages from the initial website.")
    pages_screenshots: Optional[list[PageScreenshotData]] = Field(default_factory=list,
                                                                  description="Screenshotted pages from the initial website.")
    final_website_zip: Optional[bytes] = Field(None, description="Final production website zip file.")


class State(StateBase):
    id: uuid.UUID = Field(uuid.uuid4(), description="ID of the state.")

    class Config:
        from_attributes = True
