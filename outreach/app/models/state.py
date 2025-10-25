import uuid
from typing import Optional

from sqlalchemy import Column, String, Uuid, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from app.core import Base


class State(Base):
    """
    SQLAlchemy model corresponding to the State Pydantic schema.
    """
    __tablename__ = "state"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)

    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)

    sender_name = Column(String, nullable=False)
    sender_title = Column(String, nullable=False)

    website_critique = Column(Text, nullable=False)
    demo_url = Column(String, nullable=False)
    web_agency_name = Column(String, nullable=False)
    web_agency_logo = Column(String, nullable=False)  # Assuming this is a URL

    email_sent = Column(Boolean, default=False, nullable=False)

    # Foreign key to link to the Mail table
    # This assumes a State can have one optional email
    email_id = Column(Uuid, ForeignKey("mail.id"), nullable=True)

    # Relationship to access the Mail object from a State instance
    # 'back_populates' links this to the 'state' attribute defined in Mail
    email_contents = relationship("Mail", back_populates="state")

    # Back-populates from Workflow (a State can be an initial or final state)
    workflow_as_initial: Mapped[Optional["Workflow"]] = relationship(
        back_populates="initial_state", foreign_keys="[Workflow.initial_state_id]"
    )
    workflow_as_final: Mapped[Optional["Workflow"]] = relationship(
        back_populates="final_state", foreign_keys="[Workflow.final_state_id]"
    )

    def __repr__(self):
        return f"<State(id={self.id!r}, client_name={self.client_name!r})>"
