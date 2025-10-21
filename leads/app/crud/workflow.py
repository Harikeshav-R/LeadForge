import uuid

from loguru import logger
from sqlalchemy.orm import Session

from app import models
from app import schemas


def create_workflow(db: Session, workflow: schemas.WorkflowCreate) -> models.Workflow:
    """Creates a new workflow in the database.

    Args:
        db: The SQLAlchemy database session.
        workflow: A Pydantic schema containing the data for the new workflow.

    Returns:
        The newly created and persisted Workflow model instance.
    """
    logger.info("Attempting to create a new workflow.")
    try:
        # Unpack the schema data into the Workflow model constructor.
        db_workflow = models.Workflow(**workflow.model_dump())
        logger.debug(f"Workflow data prepared for model creation: {db_workflow}")

        # Add the new object to the session, commit to the DB, and refresh the instance.
        db.add(db_workflow)
        db.commit()
        db.refresh(db_workflow)

        logger.info(f"Successfully created workflow with ID: {db_workflow.id}")
        return db_workflow
    except Exception as e:
        logger.error(f"Failed to create workflow. Rolling back transaction. Error: {e}", exc_info=True)
        db.rollback()
        raise


def get_workflow(db: Session, workflow_db_id: uuid.UUID) -> models.Workflow | None:
    """Retrieves a single workflow from the database by its UUID.

    Args:
        db: The SQLAlchemy database session.
        workflow_db_id: The UUID of the workflow to retrieve.

    Returns:
        The Workflow model instance if found, otherwise None.
    """
    logger.info(f"Fetching workflow with ID: {workflow_db_id}")
    return db.query(models.Workflow).filter(models.Workflow.id == workflow_db_id).first()


def get_workflows(db: Session, skip: int = 0, limit: int = 100) -> list[models.Workflow]:
    """Retrieves a list of workflows from the database with pagination.

    Args:
        db: The SQLAlchemy database session.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.

    Returns:
        A list of Workflow model instances.
    """
    logger.info(f"Fetching workflows with skip: {skip}, limit: {limit}")
    return db.query(models.Workflow).offset(skip).limit(limit).all()


def update_workflow(db: Session, workflow_db_id: uuid.UUID,
                    workflow_update: schemas.WorkflowUpdate) -> models.Workflow | None:
    """Updates an existing workflow in the database.

    Args:
        db: The SQLAlchemy database session.
        workflow_db_id: The UUID of the workflow to update.
        workflow_update: A Pydantic schema containing the fields to update.

    Returns:
        The updated Workflow model instance, or None if the workflow was not found.
    """
    logger.info(f"Attempting to update workflow with ID: {workflow_db_id}")
    # Find the workflow that needs to be updated.
    db_workflow = get_workflow(db, workflow_db_id)

    if not db_workflow:
        logger.warning(f"Workflow with ID {workflow_db_id} not found for update.")
        return None

    # Convert the update schema to a dictionary, only including fields that were provided.
    update_data = workflow_update.model_dump(exclude_unset=True)
    logger.debug(f"Applying update data for workflow {workflow_db_id}: {update_data}")

    # Loop through the update data and apply changes to the database model.
    for key, value in update_data.items():
        setattr(db_workflow, key, value)

    try:
        # Commit the transaction to save the changes.
        db.commit()
        db.refresh(db_workflow)
        logger.info(f"Successfully updated workflow with ID: {db_workflow.id}")
        return db_workflow
    except Exception as e:
        logger.error(f"Failed to update workflow {workflow_db_id}. Rolling back transaction. Error: {e}", exc_info=True)
        db.rollback()
        raise


def delete_workflow(db: Session, workflow_db_id: uuid.UUID) -> models.Workflow | None:
    """Deletes a workflow from the database.

    Args:
        db: The SQLAlchemy database session.
        workflow_db_id: The UUID of the workflow to delete.

    Returns:
        The deleted Workflow model instance if found and deleted, otherwise None.
    """
    logger.info(f"Attempting to delete workflow with ID: {workflow_db_id}")
    # Retrieve the workflow object to delete.
    db_workflow = get_workflow(db, workflow_db_id)

    if db_workflow:
        try:
            # If it exists, perform the deletion.
            db.delete(db_workflow)
            db.commit()
            logger.info(f"Successfully deleted workflow with ID: {workflow_db_id}")
            return db_workflow
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_db_id}. Rolling back transaction. Error: {e}",
                         exc_info=True)
            db.rollback()
            raise
    else:
        logger.warning(f"Workflow with ID {workflow_db_id} not found for deletion.")
        return None
