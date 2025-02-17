import json

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select

from src import schemas  # изменён импорт
from src.db_models import KanbanCard  # импортируем модель из БД
from src.config import get_engine, get_session  # изменение подключения к БД

# Создаем глобальный engine
engine = get_engine()

kanban_router = APIRouter()


@kanban_router.get("/kanban_pull")
def kanban_pull(request: Request):
    with open("kanban.json", "r", encoding="utf-8") as file:
        obj = json.load(file)
    return JSONResponse(content=obj)


@kanban_router.post("/kanban_push")
def kanban_push(kanban: schemas.Kanban):
    with open("kanban.json", "w", encoding="utf-8") as file:
        file.write(kanban.model_dump_json())
    return Response(status_code=200)


@kanban_router.get("/api/cards", response_model=dict[str, list[schemas.KanbanCard]])
def get_cards():
    Session = get_session(engine)
    with Session() as session:
        cards = session.scalars(select(KanbanCard)).all()
    # Сериализуем объекты через schemas.KanbanCard
    serialized_cards = [
        schemas.KanbanCard.model_validate(card).model_dump() for card in cards
    ]
    return {"cards": serialized_cards}
