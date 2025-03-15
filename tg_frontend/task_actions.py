from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import requests  # type: ignore
from aiogram.types import CallbackQuery

from aiogram.types import ReplyKeyboardRemove
import re
from crud_ops import delete_task_by_id, retrieve_room_id
from markups import statuses_markup, tasks_markup
from registercallback import register_callback  # type: ignore


from init import API_HOST


class TaskPutForm(StatesGroup):
    task = State()
    action = State()
    status = State()


router = Router()


@router.message(Command("edit"))
async def send_list(message: Message):
    chat_id = message.chat.id
    tasks = requests.get(
        url=f"http://{API_HOST}/api/cards_for_specific_room?room_id={retrieve_room_id(chat_id)}",
        headers={"accept": "application/json"},
    ).json()["cards"]

    await message.answer(
        text="Choose a task:", reply_markup=tasks_markup(tasks_json=tasks)
    )


async def show_task(query: CallbackQuery, state: FSMContext):
    await query.message.answer(text="Щас установлю стейт")
    task_id: re.Match = int(
        re.match(  # type: ignore
            pattern=r"tasks_selection:(?P<task_id>\d{1,10})", string=query.data
        ).group("task_id")
    )
    assert task_id is not None
    await state.set_state(TaskPutForm.task)

    task = requests.get(
        url=f"http://{API_HOST}/api/cards/{task_id}",
        headers={"accept": "application/json"},
    ).json()

    await state.update_data(task=task)
    actions = ("set as done", "delete", "duplicate", "change status", "cancel")

    await query.message.answer(
        text="Выбери действие: ",
        reply_markup=statuses_markup(statuses=actions),
    )
    await state.set_state(TaskPutForm.action)


register_callback(router, "tasks_selection", show_task)


@router.message(TaskPutForm.action)
async def action(message: Message, state: FSMContext):
    if "delete" in message.text:
        task = await state.get_value("task")

        delete_task_by_id(task["id"])
        await message.answer(
            text=f"Ага, удалил {task['title']}", reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    elif "set as done" in message.text:
        task = await state.get_value("task")
        task["status"] = "done"
        requests.put(
            url=f"http://{API_HOST}/api/cards/{task['id']}",
            headers={"accept": "application/json"},
            json=task,
        )
        await message.answer(
            text="Ага, типа выполнил", reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    elif "change status" in message.text:
        await message.answer(text="Выбирай статус", reply_markup=statuses_markup())
        await state.set_state(TaskPutForm.status)
    elif "cancel" in message.text:
        await state.clear()
        await message.answer(text="Отмена...", reply_markup=ReplyKeyboardRemove())
    await state.update_data(actions=message.text)


@router.message(TaskPutForm.status)
async def status(message: Message, state: FSMContext):
    task = await state.get_value("task")
    old_status = task["status"]
    task["status"] = message.text

    requests.put(
        url=f"http://{API_HOST}/api/cards/{task['id']}",
        headers={"accept": "application/json"},
        json=task,
    )

    await message.answer(
        text=f"Поменял статус {old_status} -> {task['status']}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()
