from pydantic import BaseModel, Field

from app.schemas.lead import Lead


class StateBase(BaseModel):
    city: str = Field(..., description="City name.")
    business_type: str = Field(..., description="Business type.")
    radius: int = Field(50000, description="Radius in meters for search.")
    min_rating: float = Field(0.0, description="Minimum rating for businesses.")
    max_results: int = Field(10, description="Maximum number of results to return.")

    leads: list[Lead] = Field(default_factory=list, description="Leads found in the city.")

    messages: list[str] = Field(default_factory=list, description="List of messages generated during the search.")


class StateInDBBase(StateBase):
    id: int = Field(..., description="Database ID of the state.")

    class Config:
        orm_mode = True


class State(StateInDBBase):
    pass
