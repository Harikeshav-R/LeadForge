import uuid

from loguru import logger
from sqlalchemy.orm import Session

from app import models
from app import schemas


def create_website(db: Session, website: schemas.Website) -> models.Website:
    try:
        # Create a new Website model instance from the provided schema data.
        db_website = models.Website(name=website.name, url=website.url)
        logger.debug(f"Website data prepared for website creation: {db_website}")

        # Add, commit, and refresh to persist the new website and get its DB-generated values.
        db.add(db_website)
        db.commit()
        db.refresh(db_website)

        logger.info(f"Successfully created website with ID: {db_website.id}")
        return db_website

    except Exception as e:
        logger.error(f"Failed to create website. Rolling back transaction. Error: {e}", exc_info=True)
        db.rollback()
        raise


def read_website(db: Session, website_id: uuid.UUID) -> models.Website | None:
    """Retrieves a single website from the database by its UUID.

    Args:
        db: The SQLAlchemy database session.
        website_id: The UUID of the website to retrieve.

    Returns:
        The Website model instance if found, otherwise None.
    """
    logger.info(f"Fetching website with ID: {website_id}")
    return db.query(models.Website).filter(models.Website.id == website_id).first()


def read_all_websites(db: Session, skip: int = 0, limit: int = 100) -> list[models.Website]:
    """Retrieves a list of websites from the database with pagination.

    Args:
        db: The SQLAlchemy database session.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.

    Returns:
        A list of Website model instances.
    """
    logger.info(f"Fetching websites with skip: {skip}, limit: {limit}")
    return db.query(models.Website).offset(skip).limit(limit).all()


def update_website(db: Session, website_id: uuid.UUID, website_update: schemas.WebsiteUpdate) -> models.Website | None:
    """Updates an existing website in the database.

    Args:
        db: The SQLAlchemy database session.
        website_id: The UUID of the website to update.
        website_update: A Pydantic schema containing the fields to update.

    Returns:
        The updated Website model instance, or None if the website was not found.
    """
    logger.info(f"Attempting to update website with ID: {website_id}")
    # Retrieve the existing website object.
    db_website = read_website(db, website_id)

    if not db_website:
        logger.warning(f"Website with ID {website_id} not found for update.")
        return None

    # Get a dictionary of the fields to update, excluding any that were not set.
    update_data = website_update.model_dump(exclude_unset=True)
    logger.debug(f"Applying update data for website {website_id}: {update_data}")

    # Dynamically set the attributes on the SQLAlchemy model instance.
    for key, value in update_data.items():
        setattr(db_website, key, value)

    try:
        # Commit the transaction to save the changes.
        db.commit()
        # Refresh the instance to get the latest website from the database.
        db.refresh(db_website)
        logger.info(f"Successfully updated website with ID: {db_website.id}")
        return db_website
    except Exception as e:
        logger.error(f"Failed to update website {website_id}. Rolling back transaction. Error: {e}", exc_info=True)
        db.rollback()
        raise


def delete_website(db: Session, website_id: uuid.UUID) -> models.Website | None:
    """Deletes a website from the database.

    Args:
        db: The SQLAlchemy database session.
        website_id: The UUID of the website to delete.

    Returns:
        The deleted Website model instance if found and deleted, otherwise None.
    """
    logger.info(f"Attempting to delete website with ID: {website_id}")
    # Find the website to be deleted.
    db_website = read_website(db, website_id)

    if db_website:
        try:
            # If found, delete it and commit the change.
            db.delete(db_website)
            db.commit()
            logger.info(f"Successfully deleted website with ID: {website_id}")
            return db_website
        except Exception as e:
            logger.error(f"Failed to delete website {website_id}. Rolling back transaction. Error: {e}", exc_info=True)
            db.rollback()
            raise
    else:
        logger.warning(f"Website with ID {website_id} not found for deletion.")
        return None
