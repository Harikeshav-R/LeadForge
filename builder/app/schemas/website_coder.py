from typing import Optional

from pydantic import BaseModel, Field, RootModel


class WebsiteCoderInput(BaseModel):
    prompt: str = Field(..., description="The prompt to generate the website from.")


WebsiteCoderOutput = RootModel[Optional[bytes]]
