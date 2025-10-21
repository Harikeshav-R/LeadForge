from sqlalchemy.orm import Session

from app import models
from app import schemas


def create_lead(db: Session, lead: schemas.LeadCreate):
    # Exclude nested objects that need special handling
    lead_data = lead.model_dump(exclude={'location', 'screenshots'})

    # Add flattened location data
    lead_data['lat'] = lead.location.lat
    lead_data['lng'] = lead.location.lng

    db_lead = models.Lead(**lead_data)

    # Handle the nested screenshots
    db_screenshots = [
        models.CapturedScreenshot(**screenshot.model_dump(), lead=db_lead)
        for screenshot in lead.screenshots
    ]

    db.add(db_lead)
    db.add_all(db_screenshots)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def get_lead(db: Session, lead_id: int):
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()


def get_lead_by_place_id(db: Session, place_id: str):
    return db.query(models.Lead).filter(models.Lead.place_id == place_id).first()


def get_leads(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Lead).offset(skip).limit(limit).all()


def update_lead(db: Session, lead_id: int, lead_update: schemas.LeadUpdate):
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return None

    update_data = lead_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_lead, key, value)

    db.commit()
    db.refresh(db_lead)
    return db_lead


def delete_lead(db: Session, lead_id: int):
    db_lead = get_lead(db, lead_id)
    if db_lead:
        db.delete(db_lead)
        db.commit()
    return db_lead
