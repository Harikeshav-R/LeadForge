import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.agents import create_compiled_state_graph
from app.core import get_db

router = APIRouter()


@router.post("/create-workflow", response_model=schemas.Workflow)
def create_workflow(init_state_data: schemas.StateCreate, db: Session = Depends(get_db)):
    workflow = create_compiled_state_graph()

    final_state_data = workflow.invoke(init_state_data)

    # Create Pydantic models from the results
    initial_state = schemas.State(**init_state_data.model_dump())
    final_state = schemas.State(**final_state_data)

    # Create the state first (without leads) to get an ID
    initial_state_create = schemas.StateCreate(**initial_state.model_dump(exclude={'leads', 'id'}))
    db_initial_state = crud.create_state(db, state=initial_state_create)

    # Now, create the leads associated with the initial state
    for lead in initial_state.leads:
        lead_create = schemas.LeadCreate(
            **lead.model_dump(exclude={'id', 'state_id'}),
            state_id=db_initial_state.id
        )
        crud.create_lead(db, lead=lead_create)

    # Create the final state (without leads)
    final_state_create = schemas.StateCreate(**final_state.model_dump(exclude={'leads', 'id'}))
    db_final_state = crud.create_state(db, state=final_state_create)

    # Create the leads associated with the final state
    for lead in final_state.leads:
        lead_create = schemas.LeadCreate(
            **lead.model_dump(exclude={'id', 'state_id'}),
            state_id=db_final_state.id
        )
        crud.create_lead(db, lead=lead_create)

    # --- Step 4: Save the Workflow ---

    # Now create the workflow since we have the state IDs
    workflow_create = schemas.WorkflowCreate(
        initial_state_id=db_initial_state.id,
        final_state_id=db_final_state.id,
    )

    return crud.create_workflow(db, workflow=workflow_create)


@router.get("/read-workflow/{workflow_id}", response_model=schemas.Workflow)
def read_workflow(workflow_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.read_workflow(db, workflow_id)


@router.get("/read-workflow/", response_model=list[schemas.Workflow])
def read_all_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.read_all_workflows(db, skip, limit)


@router.put("/update-workflow/{workflow_id}", response_model=schemas.Workflow)
def update_workflow(workflow_id: uuid.UUID, workflow_update: schemas.WorkflowUpdate, db: Session = Depends(get_db)):
    return crud.update_workflow(db, workflow_id, workflow_update)


@router.delete("/delete-workflow/{workflow_id}", response_model=schemas.Workflow)
def delete_workflow(workflow_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.delete_workflow(db, workflow_id)
