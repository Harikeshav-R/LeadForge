import uuid

from sqlalchemy.orm import Session

from app import models
from app import schemas


def create_workflow(db: Session, workflow: schemas.WorkflowCreate):
    db_workflow = models.Workflow(**workflow.model_dump())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def get_workflow(db: Session, workflow_db_id: uuid.UUID):
    return db.query(models.Workflow).filter(models.Workflow.id == workflow_db_id).first()


def get_workflows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Workflow).offset(skip).limit(limit).all()


def update_workflow(db: Session, workflow_db_id: uuid.UUID, workflow_update: schemas.WorkflowUpdate):
    db_workflow = get_workflow(db, workflow_db_id)
    if not db_workflow:
        return None

    update_data = workflow_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_workflow, key, value)

    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def delete_workflow(db: Session, workflow_db_id: uuid.UUID):
    db_workflow = get_workflow(db, workflow_db_id)
    if db_workflow:
        db.delete(db_workflow)
        db.commit()
    return db_workflow
