import uuid

from sqlalchemy import Column, Text, Uuid, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core import Base


class PageScreenshot(Base):
    """
    SQLAlchemy model for 'PageScreenshotData'.
    Stores a URL and its corresponding Base64-encoded screenshot.
    """
    __tablename__ = "page_screenshot_data"

    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    url = Column(String(2048), nullable=False, comment="URL of the page that was screenshotted.")
    screenshot = Column(Text, nullable=False, comment="Base64-encoded screenshot image.")

    # Foreign key to link back to the parent State
    state_id = Column(Uuid, ForeignKey("state.id"), nullable=False, index=True)

    # Many-to-One: Links this screenshot back to its parent State.
    state = relationship("State", back_populates="pages_screenshots")
