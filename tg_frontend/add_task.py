from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import requests  # type: ignore

from aiogram.types import ReplyKeyboardRemove
from markups import statuses_markup
from crud_ops import retrieve_room_id
from init import API_HOST


class TaskForm(StatesGroup):
    title_description = State()
    schedule_period = State()
    initial_status = State()


router = Router()


@router.message(Command("addtask"))
async def create_task(message: Message, state: FSMContext):
    await message.answer("Название задания:")
    await state.set_state(TaskForm.title_description)


@router.message(TaskForm.title_description)
async def task_title(message: Message, state: FSMContext):
    await state.update_data(title_description=message.text)
    await message.answer("Период оборота задания(-1 если единожды):")
    await state.set_state(TaskForm.schedule_period)


@router.message(TaskForm.schedule_period)
async def task_schedule(message: Message, state: FSMContext):
    await message.answer("Начальный статус", reply_markup=statuses_markup())
    await state.update_data(schedule_period=int(message.text))
    await state.set_state(TaskForm.initial_status)


@router.message(TaskForm.initial_status)
async def task_status(message: Message, state: FSMContext):
    await state.update_data(initial_status=message.text)

    await message.answer("Выслушал тебя, дорогой", reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    print(data)

    requests.post(
        url=f"http://{API_HOST}/api/cards",
        headers={"accept": "application/json"},
        json={
            "title": data["title_description"].split("\n")[0],
            "description": data["title_description"].split("\n")[1]
            if "\n" in data["title_description"]
            else "",
            "room_id": retrieve_room_id(message.chat.id),
            "status": data["initial_status"],
            "due_date": "string",
            "priority": "string",
            "created_at": "string",
            "period": data["schedule_period"],
            "history_records": [],
            "cooldown": "",
            "history_as_string": "",
            "days_till_todo": -1,
            "hours_till_todo": -1,
        },
    )

    await state.clear()
