import uuid
from typing import Optional

from pydantic import BaseModel, Field


class Website(BaseModel):
    name: str = Field(..., description="Name of the static website.")


class WebsiteCreate(Website):
    zip_base64: str = Field(..., description="Base64-encoded zip file of the static website.")


class WebsiteUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the static website.")


class Website(Website):
    id: uuid.UUID = Field(uuid.uuid4(), description="ID of the website.")
    url: Optional[str] = Field(None, description="URL of the deployed website.")

    class Config:
        from_attributes = True
