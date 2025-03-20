import requests  # type: ignore
from init import API_HOST


def delete_task_by_id(task_id):
    return requests.delete(url=f"http://{API_HOST}/api/cards/{task_id}")


def retrieve_room_id(chat_id):
    return requests.get(
        url=f"http://{API_HOST}/api/tgroom?telegram_chat_id={chat_id}",
        headers={"accept": "application/json"},
    ).json()["room_id"]


def tasks_for_notification(chat_id):
    return requests.get(
        url=f"http://{API_HOST}/api/room_notifications?room_id={retrieve_room_id(chat_id)}",
        headers={"accept": "application/json"},
    ).json()["cards"]


def must_notify(telegram_chat_id) -> bool:
    notify: bool = get_telegram_room(telegram_chat_id)["notify"]
    return notify


def get_telegram_room(telegram_chat_id):
    return requests.get(
        f"http://{API_HOST}/api/tgroom?telegram_chat_id={telegram_chat_id}"
    ).json()


def put_room_notifications(telegram_chat_id, turned_on):
    url = f"http://{API_HOST}/api/notify?telegram_chat_id={telegram_chat_id}&notify={str(turned_on).lower()}"
    requests.put(url)


def tasks_for_specific_chat(chat_id):
    return requests.get(
        url=f"http://{API_HOST}/api/cards_for_specific_room?room_id={retrieve_room_id(chat_id)}",
        headers={"accept": "application/json"},
    ).json()["cards"]


# def room_notifications(telegram_chat_id, notify):
#     notify= f'&notify={not notify  if notify!=None else 'null'}'
#     preferred_time = f'&preferred_time={preferred_time if preferred_time else 'null'}'
#     url = f'http://{API_HOST}/api/notify?telegram_chat_id={telegram_chat_id}{notify}{preferred_time}'
#     requests.put(url, headers={"accept": "application/json"})


def create_task(chat_id, title, desc, status, period):
    requests.post(
        url=f"http://{API_HOST}/api/cards",
        headers={"accept": "application/json"},
        json={
            "title": title,
            "description": desc,
            "room_id": retrieve_room_id(chat_id),
            "status": status,
            "due_date": "string",
            "priority": "string",
            "created_at": "string",
            "period": period,
            "history_records": [],
            "cooldown": "",
            "history_as_string": "",
            "days_till_todo": -1,
            "hours_till_todo": -1,
        },
    )
