from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class KanbanCard(Base):
    __tablename__ = "kanban_cards"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    assignee: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str | None] = mapped_column(nullable=True)
    due_date: Mapped[str | None] = mapped_column(nullable=True)
    priority: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[str | None] = mapped_column(nullable=True)
    period: Mapped[int] = mapped_column(default=-1)
    cooldown: Mapped[str] = mapped_column(default="")

    history_as_string: Mapped[str] = mapped_column(default="")
    days_till_todo: Mapped[int] = mapped_column(default=-1)
    hours_till_todo: Mapped[int] = mapped_column(default=-1)

    history_records: Mapped[list["HistoryRecord"]] = relationship(
        "HistoryRecord", back_populates="card", cascade="all, delete-orphan"
    )


class HistoryRecord(Base):
    __tablename__ = "history_records"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timestamp: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str | None] = mapped_column(nullable=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("kanban_cards.id"))
    card: Mapped["KanbanCard"] = relationship(
        "KanbanCard", back_populates="history_records"
    )
