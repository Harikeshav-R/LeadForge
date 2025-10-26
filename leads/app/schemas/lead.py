import uuid

from pydantic import BaseModel, Field

from app.schemas.visual_analysis import CapturedScreenshot


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
    # location: Location = Field(..., description="Location coordinates of the business.")
    lat: float = Field(..., description="Latitude of the business.")
    lng: float = Field(..., description="Longitude of the business.")

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
    state_id: uuid.UUID = Field(..., description="ID of the state to which the lead belongs.")


# Schema for partially updating an existing lead. All fields are optional.
class LeadUpdate(BaseModel):
    place_id: str | None = Field(None, description="ID of the place on google maps.")
    name: str | None = Field(None, description="Name of the business.")
    address: str | None = Field(None, description="Address of the business.")
    phone_number: str | None = Field(None, description="Phone number of the business.")
    website: str | None = Field(None, description="Website of the business.")
    rating: float | None = Field(None, description="Rating of the business.")
    total_ratings: int | None = Field(None, description="Total number of ratings.")
    category: str | None = Field(None, description="Category of the business.")
    price_level: int | None = Field(None, description="Price level of the business.")
    is_open: bool | None = Field(None, description="Whether the business is open.")
    # location: Location = Field(..., description="Location coordinates of the business.")
    lat: float | None = Field(None, description="Latitude of the business.")
    lng: float | None = Field(None, description="Longitude of the business.")

    emails: list[str] | None = Field(None, description="A list of unique email addresses scraped.")
    phone_numbers: list[str] | None = Field(None, description="A list of unique phone numbers scraped.")
    social_media: list[str] | None = Field(None, description="A list of unique social media profile links scraped.")

    screenshots: list[CapturedScreenshot] | None = Field(None,
                                                         description="List of base64 encoded captured screenshots for different devices.")
    website_review: str | None = Field(None, description="Business website UI/UX review from the agent.")


class Lead(LeadBase):
    id: uuid.UUID = Field(uuid.uuid4, description="ID of the lead.")
    state_id: uuid.UUID = Field(uuid.uuid4, description="ID of the state to which the lead belongs.")

    class Config:
        from_attributes = True
