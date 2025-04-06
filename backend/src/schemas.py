import datetime
import json
from pydantic import BaseModel, ConfigDict, Field, computed_field
from datetime import datetime as dt


class HistoryRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    timestamp: str
    status: str | None = None
    previous_status: str | None = None


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


class KanbanCardRequest(KanbanCard):
    pass


class KanbanCardResponse(KanbanCard):
    @computed_field
    def being_late_by(self) -> str:
        if self.status == "todo" and self.period != -1:
            last_status_date = dt.fromisoformat(self.history_records[-1].timestamp)
            td = dt.now() - last_status_date
            serialized_td = {
                "days": td.days,
                "seconds": td.seconds,
                "microseconds": td.microseconds,
                "total_seconds": td.total_seconds(),
            }
            return json.dumps(serialized_td)
        return ""

    @computed_field
    def till_todo(self) -> str:
        if self.status == "done" and self.period != -1:
            last_status_date = dt.fromisoformat(self.history_records[-1].timestamp)
            projected_date = last_status_date + datetime.timedelta(days=self.period)
            td = projected_date - dt.now()
            serialized_td = {
                "days": td.days,
                "seconds": td.seconds,
                "microseconds": td.microseconds,
                "total_seconds": td.total_seconds(),
            }
            return json.dumps(serialized_td)
        return ""

    history_records: list[HistoryRecord] = []

    @computed_field
    def beautiful_history(self) -> str:
        formatted_times = [
            dt.fromisoformat(record.timestamp).strftime("%d-%m-%y %H:%M:%S")
            for record in self.history_records
        ]
        return "\n".join(
            [
                f"{record.previous_status} -> {record.status};(at {formatted})"
                for record, formatted in zip(self.history_records, formatted_times)
            ]
        )

    @computed_field
    def beautiful_card(self) -> str:
        summary = []
        for field_name, field_info in self.model_fields.items():
            if field_name not in (
                "history_records",
                "id",
                "room_id",
                "due_date",
                "priority",
                "created_at",
            ):
                field_value = getattr(self, field_name)
                formatted_name = field_name.replace("_", " ").title()
                summary.append(f"{formatted_name}: {field_value}")
        summary.append(f"history: {self.beautiful_history}")
        return "\n".join(summary)

    id: int | None


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


class NotificationTime(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    time: str


class KanbanEnclosureForTG(BaseModel):  # response only
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    room_id: int
    telegram_chat_id: int
    notify: bool
    preferred_notification_times: list[NotificationTime]
    preferred_notification_strftime: str = "%H:%M:%S"
