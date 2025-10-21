from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CapturedScreenshot(Base):
    __tablename__ = "captured_screenshot"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device: Mapped[str]
    # Use Text instead of String for potentially very long base64 data
    image: Mapped[str] = mapped_column(Text)

    # Foreign key to link back to the Lead
    lead_id: Mapped[int] = mapped_column(ForeignKey("lead.id"))

    # The back-populating relationship
    lead: Mapped["Lead"] = relationship(back_populates="screenshots")
