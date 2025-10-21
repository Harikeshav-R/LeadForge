import uuid

from loguru import logger
from sqlalchemy.orm import Session

from app import models
from app import schemas


def create_lead(db: Session, lead: schemas.LeadCreate) -> models.Lead:
    """Creates a new lead in the database along with its associated screenshots.

    This function takes the lead creation schema, separates the lead data from the
    nested screenshot data, creates the Lead model, and then creates the
    CapturedScreenshot models, associating them with the new lead.

    Args:
        db: The SQLAlchemy database session.
        lead: A Pydantic schema containing the data for the new lead.

    Returns:
        The newly created and persisted Lead model instance.
    """
    logger.info("Attempting to create a new lead in the database.")
    try:
        # Exclude nested objects like 'screenshots' that need special handling
        # before creating the main Lead object.
        lead_data = lead.model_dump(exclude={'screenshots'})
        logger.debug(f"Lead data prepared for model creation: {lead_data}")

        db_lead = models.Lead(**lead_data)

        # Handle the nested screenshots by creating model instances for each one
        # and associating them back to the parent `db_lead` object.
        if lead.screenshots:
            logger.info(f"Creating {len(lead.screenshots)} screenshot records for the new lead.")
            db_screenshots = [
                models.CapturedScreenshot(**screenshot.model_dump(), lead=db_lead)
                for screenshot in lead.screenshots
            ]
            db.add_all(db_screenshots)

        # Add the new lead to the session.
        db.add(db_lead)
        # Commit all changes (lead and screenshots) to the database.
        db.commit()
        # Refresh the instance to get the new state from the database (e.g., generated ID).
        db.refresh(db_lead)

        logger.info(f"Successfully created lead with ID: {db_lead.id}")
        return db_lead
    except Exception as e:
        logger.error(f"Failed to create lead. Rolling back transaction. Error: {e}", exc_info=True)
        db.rollback()
        raise


def read_lead(db: Session, lead_id: uuid.UUID) -> models.Lead | None:
    """Retrieves a single lead from the database by its UUID.

    Args:
        db: The SQLAlchemy database session.
        lead_id: The UUID of the lead to retrieve.

    Returns:
        The Lead model instance if found, otherwise None.
    """
    logger.info(f"Fetching lead with ID: {lead_id}")
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()


def read_lead_by_place_id(db: Session, place_id: str) -> models.Lead | None:
    """Retrieves a single lead from the database by its Google Place ID.

    Args:
        db: The SQLAlchemy database session.
        place_id: The Google Place ID of the lead to retrieve.

    Returns:
        The Lead model instance if found, otherwise None.
    """
    logger.info(f"Fetching lead with Place ID: {place_id}", place_id)
    return db.query(models.Lead).filter(models.Lead.place_id == place_id).first()


def read_all_leads_by_place_id(db: Session, place_id: str) -> list[models.Lead] | None:
    """Retrieves a single lead from the database by its Google Place ID.

    Args:
        db: The SQLAlchemy database session.
        place_id: The Google Place ID of the lead to retrieve.

    Returns:
        The Lead model instance if found, otherwise None.
    """
    logger.info(f"Fetching all leads with Place ID: {place_id}", place_id)
    return db.query(models.Lead).filter(models.Lead.place_id == place_id).all()


def read_all_leads(db: Session, skip: int = 0, limit: int = 100) -> list[models.Lead]:
    """Retrieves a list of leads from the database with pagination.

    Args:
        db: The SQLAlchemy database session.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.

    Returns:
        A list of Lead model instances.
    """
    logger.info(f"Fetching leads with skip: {skip}, limit: {limit}")
    return db.query(models.Lead).offset(skip).limit(limit).all()


def update_lead(db: Session, lead_id: uuid.UUID, lead_update: schemas.LeadUpdate) -> models.Lead | None:
    """Updates an existing lead in the database.

    Args:
        db: The SQLAlchemy database session.
        lead_id: The UUID of the lead to update.
        lead_update: A Pydantic schema containing the fields to update.

    Returns:
        The updated Lead model instance, or None if the lead was not found.
    """
    logger.info(f"Attempting to update lead with ID: {lead_id}")
    # First, retrieve the existing lead from the database.
    db_lead = read_lead(db, lead_id)

    if not db_lead:
        logger.warning(f"Lead with ID {lead_id} not found for update.")
        return None

    # Get the update data from the Pydantic model.
    # `exclude_unset=True` ensures that only fields explicitly provided in the
    # request are included in the update data.
    update_data = lead_update.model_dump(exclude_unset=True)
    logger.debug(f"Applying update data for lead {lead_id}: {update_data}")

    # Iterate over the update data and apply the changes to the model instance.
    for key, value in update_data.items():
        setattr(db_lead, key, value)

    try:
        # Commit the changes to the database.
        db.commit()
        # Refresh the instance to reflect the updated state.
        db.refresh(db_lead)
        logger.info(f"Successfully updated lead with ID: {db_lead.id}")
        return db_lead
    except Exception as e:
        logger.error(f"Failed to update lead {lead_id}. Rolling back transaction. Error: {e}", exc_info=True)
        db.rollback()
        raise


def delete_lead(db: Session, lead_id: uuid.UUID) -> models.Lead | None:
    """Deletes a lead from the database.

    Args:
        db: The SQLAlchemy database session.
        lead_id: The UUID of the lead to delete.

    Returns:
        The deleted Lead model instance if found and deleted, otherwise None.
    """
    logger.info("Attempting to delete lead with ID: %s", lead_id)
    # Retrieve the lead to be deleted.
    db_lead = read_lead(db, lead_id)

    if db_lead:
        try:
            # Delete the object from the session and commit.
            db.delete(db_lead)
            db.commit()
            logger.info(f"Successfully deleted lead with ID: {lead_id}")
            return db_lead
        except Exception as e:
            logger.error(f"Failed to delete lead {lead_id}. Rolling back transaction. Error: {e}", e, exc_info=True)
            db.rollback()
            raise
    else:
        logger.warning(f"Lead with ID {lead_id} not found for deletion.")
        return None
