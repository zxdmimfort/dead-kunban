from pydantic import BaseModel, Field
from typing import Optional


class HistoryRecord(BaseModel):
    timestamp: str
    status: str | None = None


class KanbanCard(BaseModel):
    id: int | None = None
    title: str | None = None
    description: str | None = None
    assignee: str | None = None  # Equivalent to required=False in Marshmallow
    status: str | None = None
    dueDate: str | None = None
    priority: str | None = None  # Equivalent to required=False in Marshmallow
    createdAt: str | None = None
    period: int = Field(default=-1)  # Equivalent to missing=-1 in Marshmallow
    history: (
        list[HistoryRecord] | None
    ) = []  # Nested field with many=True in Marshmallow

    cooldown: Optional[str] = Field(
        default=""
    )  # Equivalent to missing='' in Marshmallow
    history_as_string: str | None = Field(
        default=""
    )  # Equivalent to missing='' in Marshmallow
    days_till_todo: int | None = Field(
        default=-1
    )  # Equivalent to missing=-1 in Marshmallow
    hours_till_todo: int | None = Field(
        default=-1
    )  # Equivalent to missing=-1 in Marshmallow


class Kanban(BaseModel):
    columns: list | None = None
    cards: list[KanbanCard] | None = []
