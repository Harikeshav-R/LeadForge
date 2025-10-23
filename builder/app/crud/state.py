import uuid

from sqlalchemy.orm import Session, joinedload

from app import models, schemas


def _map_pydantic_children_to_model(state_in: schemas.State, db_state: models.State):
    # --- 1. Map Scraped Pages ---
    for page_data in state_in.pages_scraped:
        # Create the PageScrapedDataModel instance
        db_page = models.PageScraped(
            url=page_data.url,
            title=page_data.title,
            meta_description=page_data.meta_description,
            paragraphs=page_data.paragraphs,
            state=db_state  # Link to the parent StateModel
        )

        # 1a. Map Headings (One-to-One)
        # SQLAlchemy handles linking this to db_page.headings
        db_headings = models.Headings(
            h1=page_data.headings.h1,
            h2=page_data.headings.h2,
            h3=page_data.headings.h3,
            h4=page_data.headings.h4,
            h5=page_data.headings.h5,
            h6=page_data.headings.h6,
            page_scraped_data=db_page  # Link to parent PageScrapedDataModel
        )

        # 1b. Map Links (One-to-Many)
        # SQLAlchemy handles appending these to db_page.links
        for link in page_data.links:
            db_link = models.Link(
                text=link.text,
                href=link.href,
                page_scraped_data=db_page  # Link to parent PageScrapedDataModel
            )

        # 1c. Map Images (One-to-Many)
        # SQLAlchemy handles appending these to db_page.images
        for image in page_data.images:
            db_image = models.Image(
                src=image.src,
                alt=image.alt,
                page_scraped_data=db_page  # Link to parent PageScrapedDataModel
            )

    # --- 2. Map Screenshots ---
    # SQLAlchemy handles appending these to db_state.pages_screenshots
    for screenshot_data in state_in.pages_screenshots:
        db_screenshot = models.PageScreenshot(
            url=screenshot_data.url,
            screenshot=screenshot_data.screenshot,
            state=db_state  # Link to the parent StateModel
        )


# --- C R U D ---

# --- CREATE ---
def create_state(db: Session, state_in: schemas.StateCreate) -> models.State:
    # 1. Create the parent StateModel object from the schema's scalar fields
    db_state = models.State(
        id=state_in.id,  # Use the ID from the Pydantic schema
        initial_website_url=state_in.initial_website_url,
        initial_website_scrape_limit=state_in.initial_website_scrape_limit,
        prompt=state_in.prompt,
        final_website_zip=state_in.final_website_zip
    )

    # 2. Use the helper to create all nested child objects
    _map_pydantic_children_to_model(schemas.State(**state_in.model_dump()), db_state)

    # 3. Add the parent object to the session.
    # The cascade setting will automatically add all children.
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state


# --- READ (Single) ---
def get_state(db: Session, state_id: uuid.UUID) -> models.State | None:
    db_state = db.query(models.State).options(
        joinedload(models.State.pages_scraped).options(
            joinedload(models.PageScraped.headings),
            joinedload(models.PageScraped.links),
            joinedload(models.PageScraped.images)
        ),
        joinedload(models.State.pages_screenshots)
    ).filter(models.State.id == state_id).first()

    return db_state


# --- READ (Multiple) ---
def get_states(db: Session, skip: int = 0, limit: int = 100) -> list[models.State]:
    """
    Retrieves a list of State records.

    NOTE: This function does NOT load the nested relationships for
    performance. Call get_state(id) to get full details for a single item.
    """
    return db.query(models.State).offset(skip).limit(limit).all()


# --- UPDATE ---
def update_state(db: Session, state_id: uuid.UUID, state_in: schemas.StateUpdate) -> models.State | None:
    """
    Updates an existing State record.

    This function performs a full replacement of the object and its
    nested children. It clears all existing children and rebuilds them
    from the 'state_in' schema.
    """
    # 1. Get the existing state, including all its children
    db_state = get_state(db, state_id)

    if not db_state:
        return None

    # 2. Update the scalar (non-relationship) fields on the parent object
    db_state.initial_website_url = state_in.initial_website_url
    db_state.initial_website_scrape_limit = state_in.initial_website_scrape_limit
    db_state.prompt = state_in.prompt
    db_state.final_website_zip = state_in.final_website_zip

    # 3. Clear the existing collections of children.
    # 'delete-orphan' cascade will trigger SQL DELETEs for these.
    db_state.pages_scraped.clear()
    db_state.pages_screenshots.clear()

    # 4. Re-map the new children from the input schema
    _map_pydantic_children_to_model(state_in, db_state)

    # 5. Commit the transaction
    db.commit()
    db.refresh(db_state)
    return db_state


# --- DELETE ---
def delete_state(db: Session, state_id: uuid.UUID) -> models.State | None:
    """
    Deletes a State record by its UUID.

    Thanks to 'cascade="all, delete-orphan"', deleting the parent
    StateModel will automatically delete all its children records from
    all related tables.
    """
    # .get() is the most efficient way to fetch by primary key
    db_state = db.get(models.State, state_id)

    if db_state:
        db.delete(db_state)
        db.commit()

    return db_state
