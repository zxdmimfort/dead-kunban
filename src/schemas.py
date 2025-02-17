from pydantic import BaseModel, ConfigDict, Field


class HistoryRecord(BaseModel):
    timestamp: str
    status: str | None = None


class KanbanCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    title: str | None = None
    description: str | None = None
    assignee: str | None = None
    status: str | None = None
    dueDate: str | None = None
    priority: str | None = None
    createdAt: str | None = None
    period: int = Field(default=-1)
    history: list[HistoryRecord] | None = []
    cooldown: str | None = Field(default="")
    history_as_string: str | None = Field(default="")
    days_till_todo: int | None = Field(default=-1)
    hours_till_todo: int | None = Field(default=-1)


class Kanban(BaseModel):
    columns: list | None = None
    cards: list[KanbanCard] | None = []
