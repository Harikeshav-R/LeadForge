from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.state import State


class WorkflowBase(BaseModel):
    workflow_id: str = Field(..., description="Unique ID of the workflow.")


# When creating a workflow, we link existing states by their IDs.
class WorkflowCreate(WorkflowBase):
    initial_state_id: int
    final_state_id: int


class WorkflowUpdate(BaseModel):
    workflow_id: Optional[str] = None
    initial_state_id: Optional[int] = None
    final_state_id: Optional[int] = None


class Workflow(WorkflowBase):
    id: int
    initial_state: State
    final_state: State

    class Config:
        orm_mode = True
