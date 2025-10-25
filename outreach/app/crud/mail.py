import uuid

from sqlalchemy.orm import Session

from app import models, schemas


def create_mail(db: Session, mail_data: schemas.MailCreate) -> models.Mail:
    db_mail = models.Mail(**mail_data.model_dump())
    db.add(db_mail)
    db.commit()
    db.refresh(db_mail)
    return db_mail


def read_mail(db: Session, mail_id: uuid.UUID) -> models.Mail | None:
    return db.query(models.Mail).filter(models.Mail.id == mail_id).first()


def read_all_mails(db: Session, skip: int = 0, limit: int = 100) -> list[models.Mail]:
    return db.query(models.Mail).offset(skip).limit(limit).all()


def update_mail(db: Session, mail_id: uuid.UUID, update_data: schemas.MailUpdate) -> models.Mail | None:
    db_mail = read_mail(db, mail_id)
    if not db_mail:
        return None

    for key, value in update_data.model_dump().items():
        setattr(db_mail, key, value)

    db.commit()
    db.refresh(db_mail)
    return db_mail


def delete_mail(db: Session, mail_id: uuid.UUID) -> models.Mail | None:
    db_mail = read_mail(db, mail_id)
    if db_mail:
        db.delete(db_mail)
        db.commit()
    return db_mail
