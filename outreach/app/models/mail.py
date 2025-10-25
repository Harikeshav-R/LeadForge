import uuid

from sqlalchemy import Column, String, Uuid, Text
from sqlalchemy.orm import relationship

from app.core import Base


class Mail(Base):
    """
    SQLAlchemy model corresponding to the Mail Pydantic schema.
    """
    __tablename__ = "mail"

    # Use sqlalchemy.Uuid for database-agnostic UUID type
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    subject = Column(String, nullable=False)
    # Use Text for potentially long email bodies
    body = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)
    recipient_email_address = Column(String, nullable=False)

    # This relationship defines the 'one' side of the one-to-one relationship
    # 'state' will be the attribute on the Mail object to access the related State
    # 'uselist=False' indicates it's a one-to-one (or many-to-one)
    state = relationship("State", back_populates="email_contents", uselist=False)

    def __repr__(self):
        return f"<Mail(id={self.id!r}, subject={self.subject!r})>"
