import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.core import get_db

router = APIRouter()


@router.post("/create-state", response_model=schemas.State)
def create_state(state: schemas.StateCreate, db: Session = Depends(get_db)):
    return crud.create_state(db, state_data=state)


@router.get("/read-state/{state_id}", response_model=schemas.State)
def read_state(state_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.read_state(db, state_id)


@router.get("/read-state/", response_model=list[schemas.State])
def read_all_states(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.read_all_states(db, skip, limit)


@router.put("/update-state/{state_id}", response_model=schemas.State)
def update_state(state_id: uuid.UUID, state_update: schemas.StateUpdate, db: Session = Depends(get_db)):
    return crud.update_state(db, state_id, state_update)


@router.delete("/delete-state/{state_id}", response_model=schemas.State)
def delete_state(state_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.delete_state(db, state_id)
