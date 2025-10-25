import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.core import get_db

router = APIRouter()


@router.post("/create-lead", response_model=schemas.Lead)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    return crud.create_lead(db, lead=lead)


@router.get("/read-lead/{lead_id}", response_model=schemas.Lead)
def read_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.read_lead(db, lead_id)


@router.get("/read-lead/", response_model=list[schemas.Lead])
def read_all_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.read_all_leads(db, skip, limit)


@router.put("/update-lead/{lead_id}", response_model=schemas.Lead)
def update_lead(lead_id: uuid.UUID, lead_update: schemas.LeadUpdate, db: Session = Depends(get_db)):
    return crud.update_lead(db, lead_id, lead_update)


@router.delete("/delete-lead/{lead_id}", response_model=schemas.Lead)
def delete_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.delete_lead(db, lead_id)
