import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.state import State


class WorkflowBase(BaseModel):
    pass


# When creating a workflow, we link existing states by their IDs.
class WorkflowCreate(WorkflowBase):
    initial_state_id: uuid.UUID = Field(..., description="ID of the initial state.")
    final_state_id: uuid.UUID = Field(..., description="ID of the final state.")


class WorkflowUpdate(BaseModel):
    initial_state_id: Optional[uuid.UUID] = Field(None, description="ID of the initial state.")
    final_state_id: Optional[uuid.UUID] = Field(None, description="ID of the final state.")


class Workflow(WorkflowBase):
    id: uuid.UUID = Field(..., description="The ID of the workflow.")
    initial_state: State = Field(..., description="The initial state.")
    final_state: State = Field(..., description="The initial state.")

    class Config:
        from_attributes = True
