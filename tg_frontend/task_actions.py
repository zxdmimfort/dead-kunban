from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import requests  # type: ignore
from aiogram.types import CallbackQuery

from aiogram.types import ReplyKeyboardRemove
import re

# from crud_ops import delete_task_by_id, retrieve_room_id, tasks_for_specific_chat
import crud_ops
from markups import just_markup, tasks_markup
from registercallback import register_callback  # type: ignore


from init import API_HOST
from utils import autoremove_markup


class TaskPutForm(StatesGroup):
    task = State()
    action = State()
    status = State()


router = Router()


@router.message(Command("edit", "изменить"))
@autoremove_markup(10)
async def send_list(message: Message):
    chat_id = message.chat.id
    tasks = crud_ops.tasks_for_specific_chat(chat_id)
    return await message.answer(text="Choose a task:", reply_markup=tasks_markup(tasks))


@router.callback_query(F.data)
async def show_task(query: CallbackQuery, state: FSMContext):
    # await query.answer(text=query.data)
    task_id = re.match(  # type: ignore
        pattern=r"tasks_selection:(?P<task_id>\d{1,10})", string=query.data
    ).group("task_id")

    assert task_id is not None
    await state.set_state(TaskPutForm.task)

    task = requests.get(
        url=f"http://{API_HOST}/api/cards/{str(task_id)}",
        headers={"accept": "application/json"},
    ).json()

    await state.update_data(task=task)
    actions = ("Сделано!", "delete", "duplicate", "change status", "cancel")

    await query.message.answer(
        text="Выбери действие: ",
        reply_markup=just_markup(statuses=actions),
    )
    await state.set_state(TaskPutForm.action)


register_callback(router, "tasks_selection", show_task)


@router.message(TaskPutForm.action)
async def action(message: Message, state: FSMContext):
    if "delete" in message.text:
        task = await state.get_value("task")

        crud_ops.delete_task_by_id(task["id"])
        await message.answer(
            text=f'Ага, удалил "{task["title"]}"', reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    elif "duplicate" in message.text:
        task = await state.get_value("task")
        del task["id"]
        requests.post(
            url=f"http://{API_HOST}/api/cards/",
            headers={"accept": "application/json"},
            json=task,
        )
        await state.clear()
        await message.answer(
            text=f'Дублировал "{task["title"]}"', reply_markup=ReplyKeyboardRemove()
        )
    elif "Сделано!" in message.text:
        task = await state.get_value("task")
        task["status"] = "done"
        requests.put(
            url=f"http://{API_HOST}/api/cards/{task['id']}",
            headers={"accept": "application/json"},
            json=task,
        )
        await message.answer(
            text=f'Ага, типа выполнил "{task["title"]}"',
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
    elif "change status" in message.text:
        await message.answer(text="Выбирай статус", reply_markup=just_markup())
        await state.set_state(TaskPutForm.status)
    elif "cancel" in message.text:
        await state.clear()
        await message.answer(text="Отмена...", reply_markup=ReplyKeyboardRemove())
    await state.update_data(actions=message.text)


@router.message(TaskPutForm.status)
async def status(message: Message, state: FSMContext):
    task = await state.get_value("task")
    old_status = task["status"]
    task["status"] = str(message.text)
    res = requests.put(
        url=f"http://{API_HOST}/api/cards/{task['id']}",
        headers={"accept": "application/json"},
        json=task,
    )

    await message.answer(
        text=f"Поменял статус {old_status} -> {res.json()['status']}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()
