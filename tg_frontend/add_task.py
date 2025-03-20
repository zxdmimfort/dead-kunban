import re
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import ReplyKeyboardRemove
from markups import just_markup
import crud_ops


class TaskForm(StatesGroup):
    title_description = State()
    schedule_period = State()
    initial_status = State()


router = Router()


@router.message(Command("addtask", "добавить_задачу"))
async def create_task(message: Message, state: FSMContext):
    match = re.match(
        pattern=r'(?P<command>/[\wа-яА-Я]+)(?P<bot_name>@\w+)?\s+"(?P<name>.*)"\s+(?P<period>\d{1,10})\s+(?P<initial_status>todo|done)',
        string=message.text,
    )

    if match:
        crud_ops.create_task(
            message.chat.id,
            match.group("name"),
            "",
            match.group("initial_status"),
            match.group("period"),
        )
        await message.answer("Выслушал", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Режим диалога... \nНазвание задания:")
        await state.set_state(TaskForm.title_description)


@router.message(TaskForm.title_description)
async def task_title(message: Message, state: FSMContext):
    await state.update_data(title_description=message.text)
    await message.answer("Период оборота задания(-1 если единожды):")
    await state.set_state(TaskForm.schedule_period)


@router.message(TaskForm.schedule_period)
async def task_schedule(message: Message, state: FSMContext):
    await message.answer("Начальный статус", reply_markup=just_markup())
    await state.update_data(schedule_period=int(message.text))
    await state.set_state(TaskForm.initial_status)


@router.message(TaskForm.initial_status)
async def task_status(message: Message, state: FSMContext):
    await state.update_data(initial_status=message.text)

    data = await state.get_data()

    crud_ops.create_task(
        message.chat.id,
        data["title_description"].split("\n")[0],
        data["title_description"].split("\n")[1]
        if "\n" in data["title_description"]
        else "",
        data["initial_status"],
        data["schedule_period"],
    )

    await state.clear()

    return await message.answer("новая задача добавлена!", markup=ReplyKeyboardRemove())
