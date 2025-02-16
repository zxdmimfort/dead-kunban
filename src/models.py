from pydantic import BaseModel

from pydantic import BaseModel, Field
from typing import List, Optional


class HistoryRecord(BaseModel):
    timestamp: str
    status: Optional[str]=None


class KanbanCard(BaseModel):
    id: Optional[int] = None
    title: str = None
    description: str = None
    assignee: str = None  # Equivalent to required=False in Marshmallow
    status: Optional[str] = None
    dueDate: Optional[str] = None
    priority: str = None  # Equivalent to required=False in Marshmallow
    createdAt: str = None
    period: int = Field(default=-1)  # Equivalent to missing=-1 in Marshmallow
    history: Optional[List[HistoryRecord]] = []  # Nested field with many=True in Marshmallow

    cooldown: Optional[str] = Field(default='')  # Equivalent to missing='' in Marshmallow
    history_as_string: Optional[str] = Field(default='')  # Equivalent to missing='' in Marshmallow
    days_till_todo: Optional[int] = Field(default=-1)  # Equivalent to missing=-1 in Marshmallow
    hours_till_todo: Optional[int] = Field(default=-1)  # Equivalent to missing=-1 in Marshmallow


class Kanban(BaseModel):
    columns: Optional[List] = None
    cards: List[KanbanCard] = []
