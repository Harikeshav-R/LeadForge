from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- Workflow Model ---
class Workflow(Base):
    __tablename__ = "workflow"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String, unique=True, index=True)

    # --- Relationships ---

    # 1-to-1: A Workflow has one initial State
    initial_state_id: Mapped[int] = mapped_column(ForeignKey("state.id"))
    initial_state: Mapped["State"] = relationship(
        back_populates="workflow_as_initial", foreign_keys=[initial_state_id]
    )

    # 1-to-1: A Workflow has one final State
    final_state_id: Mapped[int] = mapped_column(ForeignKey("state.id"))
    final_state: Mapped["State"] = relationship(
        back_populates="workflow_as_final", foreign_keys=[final_state_id]
    )
