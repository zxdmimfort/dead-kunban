from pydantic import BaseModel, ConfigDict, Field


class HistoryRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    timestamp: str
    status: str | None = None


class KanbanCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None = None
    description: str | None = None
    room_id: int | None = 0
    status: str | None = None
    due_date: str | None = None
    priority: str | None = None
    created_at: str | None = None
    period: int = Field(default=-1)
    history_records: list[HistoryRecord] | None = []
    cooldown: str | None = Field(default="")
    history_as_string: str | None = Field(default="")
    days_till_todo: int | None = Field(default=-1)
    hours_till_todo: int | None = Field(default=-1)


class Kanban(BaseModel):
    columns: list | None = None
    cards: list[KanbanCard] | None = []


class User(BaseModel):
    username: str | None = None
    password: str | None = None
    email: str | None = None
    token: str | None = None
    kanban: Kanban | None = None
    kanban_id: int | None = None


class KanbanEnclosure(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: int


class KanbanEnclosureForTG(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    room_id: int
    telegram_chat_id: int | None = None
