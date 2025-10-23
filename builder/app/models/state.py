import uuid
from typing import Optional

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.types import Uuid

from app.core import Base


class StateModel(Base):
    """
    SQLAlchemy model for the main 'State'.
    This is the root object that ties all other data together.
    """
    __tablename__ = "state"

    # Core fields from the State schema
    id = Column(Uuid, primary_key=True, default=uuid.uuid4, comment="Primary key for the state.")
    initial_website_url = Column(String(2048), nullable=False, comment="The starting URL for the scrape.")
    initial_website_scrape_limit = Column(Integer, nullable=False, default=5, comment="Max links to scrape.")
    prompt = Column(Text, nullable=True, comment="User prompt for website generation.")
    final_website_zip = Column(Text, nullable=True, comment="Base64 encoded string of the final website ZIP.")

    # --- Relationships ---

    # One-to-Many: A State can have many scraped pages.
    pages_scraped = relationship(
        "PageScrapedDataModel",
        back_populates="state",
        cascade="all, delete-orphan",
        doc="List of scraped page data associated with this state."
    )

    # One-to-Many: A State can have many page screenshots.
    pages_screenshots = relationship(
        "PageScreenshotDataModel",
        back_populates="state",
        cascade="all, delete-orphan",
        doc="List of page screenshots associated with this state."
    )

    # Back-populates from Workflow (a State can be an initial or final state)
    workflow_as_initial: Mapped[Optional["Workflow"]] = relationship(
        back_populates="initial_state", foreign_keys="[Workflow.initial_state_id]"
    )
    workflow_as_final: Mapped[Optional["Workflow"]] = relationship(
        back_populates="final_state", foreign_keys="[Workflow.final_state_id]"
    )
