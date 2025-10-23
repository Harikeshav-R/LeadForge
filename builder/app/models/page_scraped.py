import uuid

from sqlalchemy import Integer, Column, String, Text, ForeignKey, JSON, Uuid
from sqlalchemy.orm import relationship

from app.core import Base


class PageScrapedDataModel(Base):
    """
    SQLAlchemy model for 'PageScrapedData'.
    Stores all content scraped from a single URL.
    """
    __tablename__ = "page_scraped_data"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    url = Column(String(2048), nullable=False, index=True, comment="The absolute URL of the scraped page.")
    title = Column(String(512), nullable=True, comment="The page's <title> tag content.")
    meta_description = Column(Text, nullable=True, comment="The page's meta description.")

    # Storing list[str] as a JSON array.
    # This is efficient for lists of simple types.
    paragraphs = Column(JSON, default=list, comment="A JSON list of all <p> tag text.")

    # Foreign key to link back to the parent State
    state_id = Column(Uuid, ForeignKey("state.id"), nullable=False, index=True)

    # --- Relationships ---

    # Many-to-One: Links this scraped page back to its parent State.
    state = relationship("StateModel", back_populates="pages_scraped")

    # One-to-One: Each scraped page has exactly one set of headings.
    headings = relationship(
        "HeadingsModel",
        back_populates="page_scraped_data",
        uselist=False,  # Specifies this is a one-to-one relationship
        cascade="all, delete-orphan",
        doc="Headings (h1-h6) found on this page."
    )

    # One-to-Many: Each scraped page can have many links.
    links = relationship(
        "LinkModel",
        back_populates="page_scraped_data",
        cascade="all, delete-orphan",
        doc="List of hyperlinks found on this page."
    )

    # One-to-Many: Each scraped page can have many images.
    images = relationship(
        "ImageModel",
        back_populates="page_scraped_data",
        cascade="all, delete-orphan",
        doc="List of images found on this page."
    )


# --- Headings Model ---
# Stores the h1-h6 tags for a PageScrapedData.

class HeadingsModel(Base):
    """
    SQLAlchemy model for 'Headings'.
    Stores lists of heading text, linked one-to-one with a PageScrapedData.
    """
    __tablename__ = "headings"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)

    # Storing each list[str] as a JSON array.
    h1 = Column(JSON, default=list)
    h2 = Column(JSON, default=list)
    h3 = Column(JSON, default=list)
    h4 = Column(JSON, default=list)
    h5 = Column(JSON, default=list)
    h6 = Column(JSON, default=list)

    # Foreign key for the one-to-one relationship.
    # unique=True enforces that a PageScrapedData can only have one entry here.
    page_scraped_data_id = Column(
        Uuid,
        ForeignKey("page_scraped_data.id"),
        nullable=False,
        unique=True
    )

    # Back-population for the one-to-one relationship.
    page_scraped_data = relationship("PageScrapedDataModel", back_populates="headings")


# --- Link Model ---
# Stores a single hyperlink for a PageScrapedData.

class LinkModel(Base):
    """
    SQLAlchemy model for 'Link'.
    Stores a single hyperlink (text and href).
    """
    __tablename__ = "links"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False, comment="The anchor text of the link.")
    href = Column(String(2048), nullable=False, comment="The absolute URL the link points to.")

    # Foreign key to link back to the parent PageScrapedData
    page_scraped_data_id = Column(
        Uuid,
        ForeignKey("page_scraped_data.id"),
        nullable=False,
        index=True
    )

    # Many-to-One: Links this link back to its parent page.
    page_scraped_data = relationship("PageScrapedDataModel", back_populates="links")


# --- Image Model ---
# Stores a single image for a PageScrapedData.

class ImageModel(Base):
    """
    SQLAlchemy model for 'Image'.
    Stores a single image (src and alt text).
    """
    __tablename__ = "images"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    src = Column(String(2048), nullable=False, comment="The absolute source URL for the image.")
    alt = Column(Text, nullable=False, comment="The alt text for the image.")

    # Foreign key to link back to the parent PageScrapedData
    page_scraped_data_id = Column(
        Uuid,
        ForeignKey("page_scraped_data.id"),
        nullable=False,
        index=True
    )

    # Many-to-One: Links this image back to its parent page.
    page_scraped_data = (
        relationship("PageScrapedDataModel", back_populates="images"))
