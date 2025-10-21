import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base


# --- Workflow Model ---
class Workflow(Base):
    __tablename__ = "workflow"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Changed from int

    # --- Relationships ---

    # 1-to-1: A Workflow has one initial State
    initial_state_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("state.id"))  # Changed from int
    initial_state: Mapped["State"] = relationship(
        back_populates="workflow_as_initial", foreign_keys=[initial_state_id]
    )

    # 1-to-1: A Workflow has one final State
    final_state_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("state.id"))  # Changed from int
    final_state: Mapped["State"] = relationship(
        back_populates="workflow_as_final", foreign_keys=[final_state_id]
    )
