from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src import schemas  # изменён импорт
from src.db_models import (
    EnclosuresToTelegramChats,
    KanbanCard,
    KanbanEnclosure,
)  # импортируем модель из БД
from src.config import get_engine, get_session  # изменение подключения к БД

# Создаем глобальный engine
engine = get_engine()

kanban_router = APIRouter()


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


@kanban_router.get(
    "/api/rooms/", response_model=dict[str, list[schemas.KanbanEnclosure]]
)
def get_rooms():
    Session = get_session(engine)
    with Session() as session:
        rooms = session.scalars(
            select(KanbanEnclosure).options(selectinload(KanbanEnclosure.tgchat))
        ).all()

    # Сериализуем объекты через schemas.Enclosure

    serialized_rooms = [
        schemas.KanbanEnclosure.model_validate(room).model_dump() for room in rooms
    ]
    return {"rooms": serialized_rooms}


@kanban_router.post("/api/rooms/", response_model=schemas.KanbanEnclosure)
def add_room():
    Session = get_session(engine)
    with Session() as session:
        new_room = KanbanEnclosure()
        session.add(new_room)
        session.commit()
        session.refresh(new_room)
        return schemas.KanbanEnclosure.model_validate(new_room)


@kanban_router.delete("/api/rooms/{room_id}", response_model=schemas.KanbanEnclosure)
def delete_room(room_id: int):
    Session = get_session(engine)
    with Session() as session:
        room = session.get(KanbanEnclosure, room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Enclosure not found")
        session.delete(room)
        session.commit()
        return schemas.KanbanCard.model_validate(room)


@kanban_router.get("/api/tgrooms/")
def get_tg_rooms():
    Session = get_session(engine)
    with Session() as session:
        tgrooms = session.scalars(
            select(KanbanEnclosure).options(selectinload(KanbanEnclosure.tgchat))
        ).all()

        serialized_tgrooms = [room for room in tgrooms]
        print(serialized_tgrooms)
        return serialized_tgrooms


@kanban_router.post("/api/tgrooms/", response_model=schemas.KanbanEnclosureForTG)
def add_tg_room(telegram_chat_id: int):
    Session = get_session(engine)
    with Session() as session:
        new_room = KanbanEnclosure()
        session.add(new_room)
        session.flush()  # Flush to generate new_room.id without committing

        new_tg_chat = EnclosuresToTelegramChats(
            telegram_chat_id=telegram_chat_id, room_id=new_room.id
        )
        session.add(new_tg_chat)
        session.commit()

        session.refresh(new_tg_chat)

        return schemas.KanbanEnclosureForTG.model_validate(new_tg_chat)


@kanban_router.get(
    "/api/cards_for_specific_room/{room_id}",
    response_model=dict[str, list[schemas.KanbanCard]],
)
def cards_for_specific_room(room_id: int):
    Session = get_session(engine)
    with Session() as session:
        cards = session.scalars(select(KanbanCard).filter_by(room_id=room_id)).all()
        serialized_cards = [
            schemas.KanbanCard.model_validate(card).model_dump() for card in cards
        ]
        return {"cards": serialized_cards}
