from pydantic import BaseModel, Field

from app.schemas.state import State


class WorkflowBase(BaseModel):
    workflow_id: str = Field(..., description="Unique ID of the workflow.")
    initial_state: State = Field(..., description="Initial state of the workflow.")
    final_state: State = Field(..., description="Final state of the workflow.")


class WorkflowInDBBase(WorkflowBase):
    id: int = Field(..., description="Database ID of the workflow.")

    class Config:
        orm_mode = True


class Workflow(WorkflowInDBBase):
    pass
