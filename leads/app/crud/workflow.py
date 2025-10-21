from sqlalchemy.orm import Session

from app.models.workflow import Workflow as WorkflowModel
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate


def get_workflow(db: Session, workflow_db_id: int):
    return db.query(WorkflowModel).filter(WorkflowModel.id == workflow_db_id).first()


def get_workflow_by_workflow_id(db: Session, workflow_id: str):
    return db.query(WorkflowModel).filter(WorkflowModel.workflow_id == workflow_id).first()


def get_workflows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(WorkflowModel).offset(skip).limit(limit).all()


def create_workflow(db: Session, workflow: WorkflowCreate):
    db_workflow = WorkflowModel(**workflow.model_dump())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def update_workflow(db: Session, workflow_db_id: int, workflow_update: WorkflowUpdate):
    db_workflow = get_workflow(db, workflow_db_id)
    if not db_workflow:
        return None

    update_data = workflow_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_workflow, key, value)

    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def delete_workflow(db: Session, workflow_db_id: int):
    db_workflow = get_workflow(db, workflow_db_id)
    if db_workflow:
        db.delete(db_workflow)
        db.commit()
    return db_workflow
