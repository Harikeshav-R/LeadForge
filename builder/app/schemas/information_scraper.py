from typing import Optional

from pydantic import BaseModel, Field


class InformationScraperInput(BaseModel):
    url: str = Field(..., description="The base URL or domain name of the website to scrape.")
    limit: int = Field(10, description="Maximum links of the website to scrape.")


class Link(BaseModel):
    """Pydantic schema for a scraped hyperlink."""
    text: str = Field(..., description="The anchor text of the link (what the user sees).")
    href: str = Field(..., description="The absolute URL the link points to.")


class Image(BaseModel):
    """Pydantic schema for a scraped image."""
    src: str = Field(..., description="The absolute source URL for the image.")
    alt: str = Field(..., description="The alt text for the image, describing its content.")


class Headings(BaseModel):
    """Pydantic schema for scraped headings, organized by level."""
    h1: list[str] = Field(default_factory=list, description="A list of all text content from <h1> tags.")
    h2: list[str] = Field(default_factory=list, description="A list of all text content from <h2> tags.")
    h3: list[str] = Field(default_factory=list, description="A list of all text content from <h3> tags.")
    h4: list[str] = Field(default_factory=list, description="A list of all text content from <h4> tags.")
    h5: list[str] = Field(default_factory=list, description="A list of all text content from <h5> tags.")
    h6: list[str] = Field(default_factory=list, description="A list of all text content from <h6> tags.")


class PageScrapedData(BaseModel):
    """Pydantic schema for all data scraped from a single page."""
    url: str = Field(..., description="The normalized, absolute URL of the scraped page.")
    title: Optional[str] = Field(None, description="The text content of the page's <title> tag.")
    meta_description: Optional[str] = Field(None,
                                            description="The content of the page's meta description tag.")
    headings: Headings = Field(default_factory=Headings,
                               description="An object containing lists of all heading text.")
    paragraphs: list[str] = Field(default_factory=list,
                                  description="A list of all text content from <p> tags.")
    links: list[Link] = Field(default_factory=list,
                              description="A list of all scraped hyperlinks found on the page.")
    images: list[Image] = Field(default_factory=list,
                                description="A list of all scraped images found on the page.")

    # Pydantic configuration to ignore extra fields if any
    class Config:
        extra = 'ignore'


class InformationScraperOutput(BaseModel):
    """Pydantic schema for the entire crawl result (a list of pages)."""
    pages: list[PageScrapedData] = Field(..., description="A list of all PageData objects successfully scraped.")
