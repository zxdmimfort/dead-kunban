from pydantic import BaseModel

from pydantic import BaseModel, Field
from typing import List, Optional


class HistoryRecord(BaseModel):
    timestamp: str
    status: str


class KanbanCard(BaseModel):
    id: int = None
    title: str = None
    description: str = None
    assignee: Optional[str] = None  # Equivalent to required=False in Marshmallow
    status: str = None
    dueDate: str = None
    priority: Optional[str] = None  # Equivalent to required=False in Marshmallow
    createdAt: str = None
    period: int = Field(default=-1)  # Equivalent to missing=-1 in Marshmallow
    history: List[HistoryRecord] = []  # Nested field with many=True in Marshmallow
    cooldown: str = Field(default='')  # Equivalent to missing='' in Marshmallow
    history_as_string: str = Field(default='')  # Equivalent to missing='' in Marshmallow
    days_till_todo: int = Field(default=-1)  # Equivalent to missing=-1 in Marshmallow
    hours_till_todo: int = Field(default=-1)  # Equivalent to missing=-1 in Marshmallow


class Kanban(BaseModel):
    columns: Optional[str] = None
    cards: List[KanbanCard] = []
