from pydantic import BaseModel, Field


class GoogleMapsSearchInput(BaseModel):
    city: str = Field(..., description="City name to search for.")
    business_type: str = Field(None, description="Business type to filter by.")
    radius: int = Field(50000, description="Radius in meters for search.")
    min_rating: float = Field(0.0, description="Minimum rating for businesses.")
    max_results: int = Field(10, description="Maximum number of results to return.")


class Location(BaseModel):
    lat: float = Field(..., description="Latitude of the location.")
    lng: float = Field(..., description="Longitude of the location.")


class PlaceResult(BaseModel):
    place_id: str = Field(..., description="ID of the place on google maps.")
    name: str = Field(..., description="Name of the business.")
    address: str = Field(..., description="Address of the business.")
    phone_number: str | None = Field(None, description="Phone number of the business.")
    website: str | None = Field(None, description="Website of the business.")
    rating: float = Field(..., description="Rating of the business.")
    total_ratings: int = Field(..., description="Total number of ratings.")
    category: str = Field(..., description="Category of the business.")
    price_level: int = Field(..., description="Price level of the business.")
    is_open: bool = Field(..., description="Whether the business is open.")
    location: Location = Field(..., description="Location coordinates of the business.")


class SearchMetadata(BaseModel):
    city: str = Field(..., description="City name searched for.")
    business_type: str | None = Field(..., description="Business type searched for.")
    radius: int = Field(..., description="Radius in meters used for search.")
    min_rating: float = Field(..., description="Minimum rating required for results.")
    max_results: int = Field(..., description="Maximum number of results returned.")
    exclude_websites: bool = Field(..., description="Whether websites were excluded from results.")
    api_available: bool = Field(..., description="Whether the API is available.")


class GoogleMapsSearchOutput(BaseModel):
    status: str = Field(..., description="Search status.")
    total_results: int = Field(..., description="Total number of search results.")
    results: list[PlaceResult] = Field(..., description="List of search results.")
    message: str | None = Field(..., description="Error message (if any).")
    search_metadata: SearchMetadata = Field(..., description="Search metadata.")
