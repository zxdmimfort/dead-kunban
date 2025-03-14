from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import requests  # type: ignore
from aiogram.types.inline_query import InlineQuery
from aiogram.types.inline_query_result_article import InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent

from aiogram.types import ReplyKeyboardRemove
import re
from crud_ops import delete_task_by_id
from markups import statuses_markup


from init import API_HOST, bot


class TaskPutForm(StatesGroup):
    task = State()
    action = State()
    status = State()


router = Router()


@router.inline_query()
async def handle_inline_query(inline_query: InlineQuery, state: FSMContext):
    r = requests.get(
        url=f"http://{API_HOST}/api/cards", headers={"accept": "application/json"}
    )

    kanban = r.json()

    cards = kanban["cards"]

    results = [
        InlineQueryResultArticle(
            id=str(inline_id),
            title=f"{card['id']}: {card['title']}",
            description=f"status: {card['status']}\n{card['description']}",
            input_message_content=InputTextMessageContent(
                message_text=f"/task {card['id']}"
            ),
        )
        for inline_id, card in enumerate(cards)
    ]

    await bot.answer_inline_query(
        inline_query_id=inline_query.id, results=results, cache_time=1
    )


@router.message(Command("task"))
async def task_something(message: Message, state: FSMContext):
    regex: re.Match = re.match(  # type: ignore
        pattern=r"/task (?P<task_id>\d{1,10})", string=message.text
    )
    assert regex is not None
    task_id = int(regex.group("task_id"))
    await message.answer(
        text=requests.get(
            url=f"http://{API_HOST}/api/cards/{task_id}",
            headers={"accept": "application/json"},
        ).text
    )

    task = requests.get(
        url=f"http://{API_HOST}/api/cards/{task_id}",
        headers={"accept": "application/json"},
    ).json()
    await message.answer(
        text=requests.get(
            url=f"http://{API_HOST}/api/tgroom?telegram_chat_id={message.chat.id}",
            headers={"accept": "application/json"},
        ).text
    )

    tgroom = requests.get(
        url=f"http://{API_HOST}/api/tgroom?telegram_chat_id={message.chat.id}",
        headers={"accept": "application/json"},
    ).json()

    if task["room_id"] == tgroom["room_id"]:
        await message.answer(text="Ага, вы имеете доступ к такой таске")

    await state.update_data(task=task)
    actions = ("delete", "duplicate", "change_status")
    await message.answer(
        text="Выбери действие: ",
        reply_markup=statuses_markup(statuses=actions),
    )
    await state.set_state(TaskPutForm.action)

    @router.message(TaskPutForm.action)
    async def action(message: Message, state: FSMContext):
        if "delete" in message.text:
            task = await state.get_value("task")
            # await message.answer(text=f'{task_id}', reply_markup=ReplyKeyboardRemove())
            delete_task_by_id(task["id"])

            await message.answer(
                text=f"Ага, удалил {task['title']}", reply_markup=ReplyKeyboardRemove()
            )

        elif "change_status" in message.text:
            await message.answer(text="Выбирай статус", reply_markup=statuses_markup())
            await state.set_state(TaskPutForm.status)
        await state.update_data(actions=message.text)

    @router.message(TaskPutForm.status)
    async def status(message: Message, state: FSMContext):
        task = await state.get_value("task")
        task["status"] = message.text
        requests.put(
            url=f"http://{API_HOST}/api/cards/{task['id']}",
            headers={"accept": "application/json"},
            json=task,
        )
        await message.answer(
            text=f"Поменял статус {task['status']} -> {message.text}",
            reply_markup=ReplyKeyboardRemove(),
        )
