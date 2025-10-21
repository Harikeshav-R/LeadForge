from sqlalchemy import ForeignKey, String, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- Lead Model ---
class Lead(Base):
    __tablename__ = "lead"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    place_id: Mapped[str] = mapped_column(String, index=True, unique=True)
    name: Mapped[str] = mapped_column(String, index=True)
    address: Mapped[str]
    phone_number: Mapped[str | None]
    website: Mapped[str | None]
    rating: Mapped[float | None]
    total_ratings: Mapped[int | None]
    category: Mapped[str | None]
    price_level: Mapped[int | None]
    is_open: Mapped[bool | None]

    # Embedded Location fields
    lat: Mapped[float]
    lng: Mapped[float]

    # Fields for simple lists, stored as JSON
    emails: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    phone_numbers: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    social_media: Mapped[list[str] | None] = mapped_column(JSON, default=list)

    # Use Text for potentially long reviews
    website_review: Mapped[str | None] = mapped_column(Text)

    # --- Relationships ---

    # 1-to-Many: A Lead has many Screenshots
    screenshots: Mapped[list["CapturedScreenshot"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )

    # Many-to-1: Many Leads belong to one State
    state_id: Mapped[int] = mapped_column(ForeignKey("state.id"))
    state: Mapped["State"] = relationship(back_populates="leads")
