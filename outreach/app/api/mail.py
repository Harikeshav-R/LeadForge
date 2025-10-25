import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.core import get_db

router = APIRouter()


@router.post("/create-mail", response_model=schemas.Mail)
def create_mail(mail: schemas.MailCreate, db: Session = Depends(get_db)):
    return crud.create_mail(db, mail_data=mail)


@router.get("/read-mail/{mail_id}", response_model=schemas.Mail)
def read_mail(mail_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.read_mail(db, mail_id)


@router.get("/read-mail/", response_model=list[schemas.Mail])
def read_all_mails(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.read_all_mails(db, skip, limit)


@router.put("/update-mail/{mail_id}", response_model=schemas.Mail)
def update_mail(mail_id: uuid.UUID, mail_update: schemas.MailUpdate, db: Session = Depends(get_db)):
    return crud.update_mail(db, mail_id, mail_update)


@router.delete("/delete-mail/{mail_id}", response_model=schemas.Mail)
def delete_mail(mail_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.delete_mail(db, mail_id)
