from pydantic import BaseModel, Field, HttpUrl


class ContactScraperInput(BaseModel):
    url: HttpUrl = Field(..., description="The base URL or domain name of the website to scrape.")


class ContactScraperOutput(BaseModel):
    emails: list[str] = Field(default_factory=list, description="A list of unique email addresses found.")
    phone_numbers: list[str] = Field(default_factory=list, description="A list of unique phone numbers found.")
    social_media: list[HttpUrl] = Field(default_factory=list,
                                        description="A list of unique social media profile links found.")
