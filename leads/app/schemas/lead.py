from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.visual_analysis import CapturedScreenshot
from app.schemas.google_maps_search import Location


class LeadBase(BaseModel):
    place_id: str = Field(..., description="ID of the place on google maps.")
    name: str = Field(..., description="Name of the business.")
    address: str = Field(..., description="Address of the business.")
    phone_number: str | None = Field(None, description="Phone number of the business.")
    website: str | None = Field(None, description="Website of the business.")
    rating: float | None = Field(None, description="Rating of the business.")
    total_ratings: int | None = Field(None, description="Total number of ratings.")
    category: str | None = Field(None, description="Category of the business.")
    price_level: int | None = Field(None, description="Price level of the business.")
    is_open: bool | None = Field(None, description="Whether the business is open.")
    location: Location = Field(..., description="Location coordinates of the business.")

    emails: list[str] = Field(default_factory=list, description="A list of unique email addresses scraped.")
    phone_numbers: list[str] = Field(default_factory=list, description="A list of unique phone numbers scraped.")
    social_media: list[str] = Field(default_factory=list,
                                    description="A list of unique social media profile links scraped.")

    screenshots: list[CapturedScreenshot] = Field(default_factory=list,
                                                  description="List of base64 encoded captured screenshots for different devices.")
    website_review: str = Field(None, description="Business website UI/UX review from the agent.")


# Schema for creating a new lead in the DB.
# It requires a state_id to link it to a State.
class LeadCreate(LeadBase):
    state_id: int


# Schema for partially updating an existing lead. All fields are optional.
class LeadUpdate(BaseModel):
    place_id: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    total_ratings: Optional[int] = None
    category: Optional[str] = None
    price_level: Optional[int] = None
    is_open: Optional[bool] = None
    location: Optional[Location] = None
    emails: Optional[list[str]] = None
    phone_numbers: Optional[list[str]] = None
    social_media: Optional[list[str]] = None
    screenshots: Optional[list[CapturedScreenshot]] = None
    website_review: Optional[str] = None


class Lead(LeadBase):
    id: int
    state_id: int

    class Config:
        orm_mode = True
