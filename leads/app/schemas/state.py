import uuid
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
    city: Optional[str] = Field(None, description="City name.")
    business_type: Optional[str] = Field(None, description="Business type.")
    radius: Optional[int] = Field(None, description="Radius in meters for search.")
    min_rating: Optional[float] = Field(None, description="Minimum rating for businesses.")
    max_results: Optional[int] = Field(None, description="Maximum number of results to return.")
    messages: Optional[list[str]] = Field(None, description="List of messages generated during the search.")


class State(StateBase):
    id: uuid.UUID = Field(uuid.uuid4(), description="ID of the state.")
    leads: list[Lead] = Field(default_factory=list, description="Leads found in the city.")

    class Config:
        from_attributes = True
