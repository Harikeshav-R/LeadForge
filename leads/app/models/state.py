from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- State Model ---
class State(Base):
    __tablename__ = "state"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city: Mapped[str]
    business_type: Mapped[str]
    radius: Mapped[int] = mapped_column(default=50000)
    min_rating: Mapped[float] = mapped_column(default=0.0)
    max_results: Mapped[int] = mapped_column(default=10)

    # Simple list of messages, stored as JSON
    messages: Mapped[list[str] | None] = mapped_column(JSON, default=list)

    # --- Relationships ---

    # 1-to-Many: A State has many Leads
    leads: Mapped[list["Lead"]] = relationship(
        back_populates="state", cascade="all, delete-orphan"
    )

    # Back-populates from Workflow (a State can be an initial or final state)
    workflow_as_initial: Mapped["Workflow" | None] = relationship(
        back_populates="initial_state", foreign_keys="[Workflow.initial_state_id]"
    )
    workflow_as_final: Mapped["Workflow" | None] = relationship(
        back_populates="final_state", foreign_keys="[Workflow.final_state_id]"
    )
