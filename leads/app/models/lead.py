import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base


# --- Lead Model ---
class Lead(Base):
    __tablename__ = "lead"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Changed from int
    place_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    address: Mapped[str]
    phone_number: Mapped[Optional[str]]
    website: Mapped[Optional[str]]
    rating: Mapped[Optional[float]]
    total_ratings: Mapped[Optional[int]]
    category: Mapped[Optional[str]]
    price_level: Mapped[Optional[int]]
    is_open: Mapped[Optional[bool]]

    # Embedded Location fields
    lat: Mapped[float]
    lng: Mapped[float]

    # Fields for simple lists, stored as JSON
    emails: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    phone_numbers: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    social_media: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)

    # Use Text for potentially long reviews
    website_review: Mapped[Optional[str]] = mapped_column(Text)

    # --- Relationships ---

    # 1-to-Many: A Lead has many Screenshots
    screenshots: Mapped[list["CapturedScreenshot"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )

    # Many-to-1: Many Leads belong to one State
    state_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("state.id"))  # Changed from int
    state: Mapped["State"] = relationship(back_populates="leads")
