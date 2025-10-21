from sqlalchemy.orm import Session

from app import models
from app import schemas


def create_state(db: Session, state: schemas.StateCreate):
    db_state = models.State(**state.model_dump())
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state


def get_state(db: Session, state_id: int):
    return db.query(models.State).filter(models.State.id == state_id).first()


def get_states(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.State).offset(skip).limit(limit).all()


def update_state(db: Session, state_id: int, state_update: schemas.StateUpdate):
    db_state = get_state(db, state_id)
    if not db_state:
        return None

    update_data = state_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_state, key, value)

    db.commit()
    db.refresh(db_state)
    return db_state


def delete_state(db: Session, state_id: int):
    db_state = get_state(db, state_id)
    if db_state:
        db.delete(db_state)
        db.commit()
    return db_state
