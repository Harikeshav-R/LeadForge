import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base


class CapturedScreenshot(Base):
    __tablename__ = "captured_screenshot"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Changed from int
    device: Mapped[str]
    # Use Text instead of String for potentially very long base64 data
    image: Mapped[str] = mapped_column(Text)

    # Foreign key to link back to the Lead
    lead_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lead.id"))  # Changed from int

    # The back-populating relationship
    lead: Mapped["Lead"] = relationship(back_populates="screenshots")
