from pydantic import BaseModel, Field, HttpUrl, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class ContactScraperInput(BaseModel):
    url: HttpUrl = Field(..., description="The base URL or domain name of the website to scrape.")


class ContactScraperOutput(BaseModel):
    emails: list[EmailStr] = Field(default_factory=list, description="A list of unique email addresses found.")
    phone_numbers: list[PhoneNumber] = Field(default_factory=list, description="A list of unique phone numbers found.")
    social_media: list[HttpUrl] = Field(default_factory=list,
                                        description="A list of unique social media profile links found.")
