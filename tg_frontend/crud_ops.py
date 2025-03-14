import requests  # type: ignore
from init import API_HOST


def delete_task_by_id(task_id):
    return requests.delete(url=f"http://{API_HOST}/api/cards/{task_id}")


def retrieve_room_id(chat_id: int) -> int:  # type: ignore
    r = requests.get(
        url=f"http://{API_HOST}/api/tgroom/?telegram_chat_id={chat_id}",
        headers={"accept": "application/json"},
    )

    def telegram_chat_room(room, telegram_chat_id):
        room["tgchat"]["telegram_chat_id"] == telegram_chat_id

    for room in r.json():
        if telegram_chat_room(room, chat_id):
            return int(room["id"])
