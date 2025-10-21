from sqlalchemy.orm import Session

from app.models.state import State as StateModel
from app.schemas.state import StateCreate, StateUpdate


def get_state(db: Session, state_id: int):
    return db.query(StateModel).filter(StateModel.id == state_id).first()


def get_states(db: Session, skip: int = 0, limit: int = 100):
    return db.query(StateModel).offset(skip).limit(limit).all()


def create_state(db: Session, state: StateCreate):
    db_state = StateModel(**state.model_dump())
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state


def update_state(db: Session, state_id: int, state_update: StateUpdate):
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
