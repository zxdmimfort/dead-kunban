import json

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
        cards = session.scalars(
            select(KanbanCard).options(selectinload(KanbanCard.history_records))
        ).all()
    # Сериализуем объекты через schemas.KanbanCard
    serialized_cards = [
        schemas.KanbanCard.model_validate(card).model_dump() for card in cards
    ]
    return {"cards": serialized_cards}


@kanban_router.post("/api/cards", response_model=schemas.KanbanCard)
def add_card(card: schemas.KanbanCard):
    Session = get_session(engine)
    with Session() as session:
        new_card = KanbanCard(**card.model_dump(exclude_unset=True))
        session.add(new_card)
        session.commit()
        session.refresh(new_card)
        return schemas.KanbanCard.model_validate(new_card)


@kanban_router.delete("/api/cards/{card_id}", response_model=schemas.KanbanCard)
def delete_card(card_id: int):
    Session = get_session(engine)
    with Session() as session:
        card = session.get(KanbanCard, card_id)
        if card is None:
            raise HTTPException(status_code=404, detail="Card not found")
        session.delete(card)
        session.commit()
        return schemas.KanbanCard.model_validate(card)


@kanban_router.put("/api/cards/{card_id}", response_model=schemas.KanbanCard)
def update_card(card_id: int, card_update: schemas.KanbanCard):
    Session = get_session(engine)
    with Session() as session:
        card = session.get(KanbanCard, card_id)
        if card is None:
            raise HTTPException(status_code=404, detail="Card not found")
        update_data = card_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(card, key, value)
        session.commit()
        session.refresh(card)
        return schemas.KanbanCard.model_validate(card)
