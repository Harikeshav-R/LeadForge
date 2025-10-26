import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas import PageScrapedData
from app.schemas.page_screenshotter import PageScreenshotData


class StateBase(BaseModel):
    initial_website_url: str = Field(..., description="The URL of the initial website to scrape and recreate.")
    initial_website_scrape_limit: int = Field(5, description="Maximum links of the website to scrape.")
    prompt: str | None = Field(None, description="The prompt to generate the website from.")
    pages_scraped: list[PageScrapedData] = Field(default_factory=list,
                                                 description="Scraped pages from the initial website.")
    pages_screenshots: list[PageScreenshotData] = Field(default_factory=list,
                                                        description="Screenshotted pages from the initial website.")
    final_website_zip: str | None = Field(None, description="Final production website zip file in base64.")


class StateCreate(StateBase):
    pass


class StateUpdate(BaseModel):
    initial_website_url: Optional[str] = Field(None,
                                               description="The URL of the initial website to scrape and recreate.")
    initial_website_scrape_limit: Optional[int] = Field(10, description="Maximum links of the website to scrape.")
    prompt: Optional[str] = Field(None, description="The prompt to generate the website from.")
    pages_scraped: Optional[list[PageScrapedData]] = Field(default_factory=list,
                                                           description="Scraped pages from the initial website.")
    pages_screenshots: Optional[list[PageScreenshotData]] = Field(default_factory=list,
                                                                  description="Screenshotted pages from the initial website.")
    final_website_zip: Optional[str] = Field(None, description="Final production website zip file in base64.")


class State(StateBase):
    id: uuid.UUID = Field(uuid.uuid4, description="ID of the state.")

    class Config:
        from_attributes = True
