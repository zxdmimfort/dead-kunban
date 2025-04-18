from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional


class Base(DeclarativeBase):
    pass


class KanbanCard(Base):
    __tablename__ = "kanban_cards"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)

    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    room: Mapped[Optional["KanbanEnclosure"]] = relationship(
        "KanbanEnclosure", back_populates="kanban_cards"
    )

    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User", back_populates="kanban_cards"
    )
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
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str | None] = mapped_column(nullable=True)
    previous_status: Mapped[str | None] = mapped_column(nullable=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("kanban_cards.id"))
    card: Mapped["KanbanCard"] = relationship(
        "KanbanCard", back_populates="history_records"
    )


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(nullable=True, unique=True)
    password: Mapped[str | None] = mapped_column(nullable=True)
    email: Mapped[str | None] = mapped_column(nullable=True, unique=True)
    token: Mapped[str | None] = mapped_column(nullable=True)
    kanban_cards: Mapped[list["KanbanCard"]] = relationship(
        "KanbanCard", back_populates="assignee"
    )


class KanbanEnclosure(Base):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    tgchat: Mapped["EnclosuresToTelegramChats"] = relationship(
        back_populates="room", uselist=False, cascade="all, delete-orphan"
    )
    kanban_cards: Mapped[list["KanbanCard"]] = relationship(
        "KanbanCard", back_populates="room"
    )


class NotificationTime(Base):
    __tablename__ = "notification_times"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    time: Mapped[str] = mapped_column()
    tgchat_id: Mapped[str] = mapped_column(ForeignKey("tgchats.id"))


class EnclosuresToTelegramChats(Base):
    __tablename__ = "tgchats"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    telegram_chat_id: Mapped[int | None] = mapped_column(unique=True)
    notify: Mapped[bool] = mapped_column()

    preferred_notification_times: Mapped[list["NotificationTime"]] = relationship(
        cascade="all, delete-orphan"
    )

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["KanbanEnclosure"] = relationship(back_populates="tgchat")
