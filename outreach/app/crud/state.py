import uuid

from sqlalchemy.orm import Session

from app import models, schemas


def create_state(db: Session, state_data: schemas.StateCreate) -> models.State:
    """
    Create a new State record, automatically creating
    and linking an email if 'email_contents' data is provided.
    """

    state_data = state_data.model_dump()
    email_data = state_data.pop('email_contents', None)
    db_state = models.State(**state_data.model_dump())

    if email_data:
        db_email = models.Mail(**email_data)
        db_state.email_contents = db_email
        db.add(db_email)

    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state


def get_state(db: Session, state_id: uuid.UUID) -> models.State | None:
    """
    Retrieve a single State record by its ID.
    """
    return db.query(models.State).filter(models.State.id == state_id).first()


def get_states(db: Session, skip: int = 0, limit: int = 100) -> list[models.State]:
    """
    Retrieve a list of State records with pagination.
    """
    return db.query(models.State).offset(skip).limit(limit).all()


def update_state(db: Session, state_id: uuid.UUID, update_data: schemas.StateUpdate) -> models.State | None:
    """
    Update an existing State record.
    Can also update the linked email by passing 'email_contents' in update_data.
    """
    update_data = update_data.model_dump()

    db_state = get_state(db, state_id)

    if not db_state:
        return None

    email_data = update_data.pop('email_contents', None)

    # Update State fields
    for key, value in update_data.items():
        setattr(db_state, key, value)

    # Update or create linked email
    if email_data:
        if db_state.email_contents:
            # Update existing linked email
            for key, value in email_data.items():
                setattr(db_state.email_contents, key, value)
        else:
            # Create a new email and link it
            db_email = models.Mail(**email_data)
            db_state.email_contents = db_email
            db.add(db_email)

    db.commit()
    db.refresh(db_state)
    return db_state


def delete_state(db: Session, state_id: uuid.UUID) -> models.State | None:
    """
    Delete a State record and its associated Mail record.
    """
    db_state = get_state(db, state_id)
    if db_state:
        if db_state.email_contents:
            # Delete the associated mail first
            db.delete(db_state.email_contents)
        db.delete(db_state)
        db.commit()
    return db_state
