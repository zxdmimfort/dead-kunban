from typing import Any
from fastapi import APIRouter, HTTPException
from sqlalchemy import Sequence, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import selectinload
from datetime import datetime as dt, timedelta

from src import schemas  # изменён импорт
from src.db_models import (
    EnclosuresToTelegramChats,
    HistoryRecord,
    KanbanCard,
    KanbanEnclosure,
    NotificationTime,
)  # импортируем модель из БД
from src.config import get_engine, get_session  # изменение подключения к БД

# Создаем глобальный engine
engine = get_engine()

kanban_router = APIRouter()


@kanban_router.get(
    "/api/room_notifications",
    response_model=dict[str, list[schemas.KanbanCardResponse]],
)
def room_notifications(room_id: int):
    Session = get_session(engine)
    with Session() as session:
        cards: Sequence[KanbanCard] = session.scalars(
            select(KanbanCard)
            .options(selectinload(KanbanCard.history_records))
            .filter_by(room_id=room_id)
        ).all()
        ready = []
        for card in cards:
            if card.status == "done" and card.period != -1:
                last_status_date = dt.fromisoformat(card.history_records[-1].timestamp)
                projected_date = last_status_date + timedelta(days=card.period)
                if dt.now() >= projected_date:
                    status_todo = "todo"
                    new_history_record = HistoryRecord(
                        card_id=card.id,
                        timestamp=dt.now().isoformat(),
                        status=status_todo,
                        previous_status=card.status,
                    )
                    setattr(
                        card,
                        "history_records",
                        [*card.history_records, new_history_record],
                    )
                    card.status = status_todo
                    ready.append(card)

            if card.status == "todo":
                ready.append(card)

            session.commit()
            session.refresh(card)

        serialized_cards = [
            schemas.KanbanCardResponse.model_validate(card).model_dump()
            for card in ready
        ]
        return {"cards": serialized_cards}


@kanban_router.get(
    "/api/cards", response_model=dict[str, list[schemas.KanbanCardResponse]]
)
def get_cards():
    Session = get_session(engine)
    with Session() as session:
        cards = session.scalars(
            select(KanbanCard).options(selectinload(KanbanCard.history_records))
        ).all()
    # Сериализуем объекты через schemas.KanbanCard
    serialized_cards = [
        schemas.KanbanCardResponse.model_validate(card).model_dump() for card in cards
    ]
    return {"cards": serialized_cards}


@kanban_router.get("/api/cards/{card_id}", response_model=schemas.KanbanCardResponse)
def get_card_by_id(card_id: int):
    Session = get_session(engine)
    with Session() as session:
        try:
            card = session.scalars(
                select(KanbanCard)
                .options(selectinload(KanbanCard.history_records))
                .where(KanbanCard.id == card_id)
            ).one()
            return schemas.KanbanCardResponse.model_validate(card).model_dump()
        except NoResultFound:
            return None


@kanban_router.post("/api/cards", response_model=schemas.KanbanCardResponse)
def add_card(card: schemas.KanbanCardRequest):
    Session = get_session(engine)
    with Session() as session:
        new_card = KanbanCard(**card.model_dump(exclude_unset=True))

        new_history_record = HistoryRecord(
            card_id=new_card.id,
            timestamp=dt.now().isoformat(),
            status=new_card.status,
            previous_status=None,
        )
        new_card.history_records = [new_history_record]
        session.add(new_card)

        session.commit()
        session.refresh(new_card)
        return schemas.KanbanCardResponse.model_validate(new_card)


@kanban_router.delete("/api/cards/{card_id}", response_model=schemas.KanbanCardResponse)
def delete_card(card_id: int):
    Session = get_session(engine)
    with Session() as session:
        card = session.get(KanbanCard, card_id)
        if card is None:
            raise HTTPException(status_code=404, detail="Card not found")
        session.delete(card)
        session.commit()
        return schemas.KanbanCardResponse.model_validate(card)


@kanban_router.put("/api/cards/{card_id}", response_model=schemas.KanbanCardResponse)
def update_card(card_id: int, card_update: schemas.KanbanCardRequest):
    Session = get_session(engine)
    with Session() as session:
        # card = session.get(KanbanCard, card_id)
        card = session.scalars(
            select(KanbanCard)
            .options(selectinload(KanbanCard.history_records))
            .where(KanbanCard.id == card_id)
        ).one()

        if card is None:
            raise HTTPException(status_code=404, detail="Card not found")

        update_data: dict[str, Any] = card_update.model_dump(exclude_unset=True)

        new_status = update_data["status"]
        old_status = card.status

        new_history_record = HistoryRecord(
            card_id=card.id,
            timestamp=dt.now().isoformat(),
            status=new_status,
            previous_status=old_status,
        )
        update_data["history_records"] = [*card.history_records, new_history_record]

        for key, value in update_data.items():
            setattr(card, key, value)
        session.commit()
        session.refresh(card)
        return schemas.KanbanCardResponse.model_validate(card)


@kanban_router.get(
    "/api/rooms/", response_model=dict[str, list[schemas.KanbanEnclosure]]
)
def get_rooms():
    Session = get_session(engine)
    with Session() as session:
        rooms = session.scalars(
            select(KanbanEnclosure).options(selectinload(KanbanEnclosure.tgchat))
        ).all()

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


@kanban_router.get("/api/tgroom", response_model=schemas.KanbanEnclosureForTG)
def get_tg_rooms(telegram_chat_id: int):
    Session = get_session(engine)
    with Session() as session:
        try:
            tgroom = session.scalars(
                select(EnclosuresToTelegramChats)
                .options(
                    selectinload(EnclosuresToTelegramChats.preferred_notification_times)
                )
                .filter_by(telegram_chat_id=telegram_chat_id)
            ).one()

            return schemas.KanbanEnclosureForTG.model_validate(tgroom)
        except NoResultFound:
            print("No room found")
            return add_tg_room(telegram_chat_id)
        except MultipleResultsFound:
            print("Multiple rooms found")


@kanban_router.post("/api/tgroom/", response_model=schemas.KanbanEnclosureForTG)
def add_tg_room(telegram_chat_id: int):
    Session = get_session(engine)
    with Session() as session:
        new_room = KanbanEnclosure()
        session.add(new_room)
        session.flush()  # Flush to generate new_room.id without committing

        new_tg_chat = EnclosuresToTelegramChats(
            telegram_chat_id=telegram_chat_id,
            room_id=new_room.id,
            notify=False,
        )

        default_notification_time = NotificationTime(
            time="08:00:00", tgchat_id=new_tg_chat.id
        )
        new_tg_chat.preferred_notification_times.append(default_notification_time)
        session.add(new_tg_chat)

        session.commit()

        session.refresh(new_tg_chat)

        return schemas.KanbanEnclosureForTG.model_validate(new_tg_chat)


@kanban_router.get(
    "/api/cards_for_specific_room",
    response_model=dict[str, list[schemas.KanbanCardResponse]],
)
def cards_for_specific_room(room_id: int):
    Session = get_session(engine)
    with Session() as session:
        cards = session.scalars(select(KanbanCard).filter_by(room_id=room_id)).all()
        serialized_cards = [
            schemas.KanbanCardResponse.model_validate(card).model_dump()
            for card in cards
        ]
        return {"cards": serialized_cards}


@kanban_router.put("/api/notify", response_model=schemas.KanbanEnclosureForTG)
def update_notify_flag(telegram_chat_id: int, notify: bool):
    Session = get_session(engine)
    with Session() as session:
        card_update = session.scalars(
            select(EnclosuresToTelegramChats).where(
                EnclosuresToTelegramChats.telegram_chat_id == telegram_chat_id
            )
        ).one()

        if card_update is None:
            raise HTTPException(status_code=404, detail="Card not found")

        card_update.notify = notify

        session.commit()
        session.refresh(card_update)
        return schemas.KanbanEnclosureForTG.model_validate(card_update)


@kanban_router.put(
    "/api/set_preferred_notification_time", response_model=schemas.KanbanEnclosureForTG
)
def set_preferred_notification_time(
    telegram_chat_id: int, preferred_notification_times: list[schemas.NotificationTime]
):
    Session = get_session(engine)
    with Session() as session:
        tgchat = session.scalars(
            select(EnclosuresToTelegramChats).where(
                EnclosuresToTelegramChats.telegram_chat_id == telegram_chat_id
            )
        ).one()

        if tgchat is None:
            raise HTTPException(status_code=404, detail="Card not found")
        tgchat.preferred_notification_times = []
        for time in preferred_notification_times:
            tgchat.preferred_notification_times.append(
                NotificationTime(tgchat_id=tgchat.id, time=time.time)
            )

        session.commit()
        session.refresh(tgchat)
        return schemas.KanbanEnclosureForTG.model_validate(tgchat)
