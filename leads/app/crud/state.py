import uuid

from loguru import logger
from sqlalchemy.orm import Session

from app import models
from app import schemas


def create_state(db: Session, state: schemas.StateCreate) -> models.State:
    """Creates a new state in the database.

    Args:
        db: The SQLAlchemy database session.
        state: A Pydantic schema containing the data for the new state.

    Returns:
        The newly created and persisted State model instance.
    """
    logger.info("Attempting to create a new state.")
    try:
        # Create a new State model instance from the provided schema data.
        db_state = models.State(**state.model_dump())
        logger.debug(f"State data prepared for model creation: {db_state}")

        # Add, commit, and refresh to persist the new state and get its DB-generated values.
        db.add(db_state)
        db.commit()
        db.refresh(db_state)

        logger.info(f"Successfully created state with ID: {db_state.id}")
        return db_state
    except Exception as e:
        logger.error(f"Failed to create state. Rolling back transaction. Error: {e}", exc_info=True)
        db.rollback()
        raise


def get_state(db: Session, state_id: uuid.UUID) -> models.State | None:
    """Retrieves a single state from the database by its UUID.

    Args:
        db: The SQLAlchemy database session.
        state_id: The UUID of the state to retrieve.

    Returns:
        The State model instance if found, otherwise None.
    """
    logger.info(f"Fetching state with ID: {state_id}")
    return db.query(models.State).filter(models.State.id == state_id).first()


def get_states(db: Session, skip: int = 0, limit: int = 100) -> list[models.State]:
    """Retrieves a list of states from the database with pagination.

    Args:
        db: The SQLAlchemy database session.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.

    Returns:
        A list of State model instances.
    """
    logger.info(f"Fetching states with skip: {skip}, limit: {limit}")
    return db.query(models.State).offset(skip).limit(limit).all()


def update_state(db: Session, state_id: uuid.UUID, state_update: schemas.StateUpdate) -> models.State | None:
    """Updates an existing state in the database.

    Args:
        db: The SQLAlchemy database session.
        state_id: The UUID of the state to update.
        state_update: A Pydantic schema containing the fields to update.

    Returns:
        The updated State model instance, or None if the state was not found.
    """
    logger.info(f"Attempting to update state with ID: {state_id}")
    # Retrieve the existing state object.
    db_state = get_state(db, state_id)

    if not db_state:
        logger.warning(f"State with ID {state_id} not found for update.")
        return None

    # Get a dictionary of the fields to update, excluding any that were not set.
    update_data = state_update.model_dump(exclude_unset=True)
    logger.debug(f"Applying update data for state {state_id}: {update_data}")

    # Dynamically set the attributes on the SQLAlchemy model instance.
    for key, value in update_data.items():
        setattr(db_state, key, value)

    try:
        # Commit the transaction to save the changes.
        db.commit()
        # Refresh the instance to get the latest state from the database.
        db.refresh(db_state)
        logger.info(f"Successfully updated state with ID: {db_state.id}")
        return db_state
    except Exception as e:
        logger.error(f"Failed to update state {state_id}. Rolling back transaction. Error: {e}", exc_info=True)
        db.rollback()
        raise


def delete_state(db: Session, state_id: uuid.UUID) -> models.State | None:
    """Deletes a state from the database.

    Args:
        db: The SQLAlchemy database session.
        state_id: The UUID of the state to delete.

    Returns:
        The deleted State model instance if found and deleted, otherwise None.
    """
    logger.info(f"Attempting to delete state with ID: {state_id}")
    # Find the state to be deleted.
    db_state = get_state(db, state_id)

    if db_state:
        try:
            # If found, delete it and commit the change.
            db.delete(db_state)
            db.commit()
            logger.info(f"Successfully deleted state with ID: {state_id}")
            return db_state
        except Exception as e:
            logger.error(f"Failed to delete state {state_id}. Rolling back transaction. Error: {e}", exc_info=True)
            db.rollback()
            raise
    else:
        logger.warning(f"State with ID {state_id} not found for deletion.")
        return None
