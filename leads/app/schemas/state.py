from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.lead import Lead


class StateBase(BaseModel):
    city: str = Field(..., description="City name.")
    business_type: str = Field(..., description="Business type.")
    radius: int = Field(50000, description="Radius in meters for search.")
    min_rating: float = Field(0.0, description="Minimum rating for businesses.")
    max_results: int = Field(10, description="Maximum number of results to return.")
    messages: list[str] = Field(default_factory=list, description="List of messages generated during the search.")


class StateCreate(StateBase):
    pass


class StateUpdate(BaseModel):
    city: Optional[str] = None
    business_type: Optional[str] = None
    radius: Optional[int] = None
    min_rating: Optional[float] = None
    max_results: Optional[int] = None
    messages: Optional[list[str]] = None


class State(StateBase):
    id: int
    leads: list[Lead] = Field(default_factory=list, description="Leads found in the city.")

    class Config:
        orm_mode = True
