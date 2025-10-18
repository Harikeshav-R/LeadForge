from pydantic import BaseModel, Field

from app.schemas.lead import Lead


class State(BaseModel):
    city: str = Field(..., description="City name.")
    business_type: str = Field(..., description="Business type.")
    leads: list[Lead] = Field(..., description="Leads found in the city.")

    messages: list[str] = Field(default_factory=list, description="List of messages generated during the search.")
