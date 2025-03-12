import asyncio
import datetime
from math import ceil
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from typing import Callable, Awaitable
import os
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import requests  # type: ignore
from aiogram.types.inline_query import InlineQuery
from aiogram.types.inline_query_result_article import InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent

from aiogram.types import KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import re

load_dotenv(dotenv_path="token.env")
BOT_TOKEN: str = os.getenv("TG_KEY") or ""
CREDENTIALS: str = os.getenv("GIGA_KEY") or ""

if not BOT_TOKEN or not CREDENTIALS:
    raise ValueError("Missing one of the secret keys")

admins: tuple[str, ...] = ("aoi_dev", "mimfort")


class TaskForm(StatesGroup):
    title_description = State()
    schedule_period = State()
    initial_status = State()


reminder_cooldown: dict[int, int] = {}


statuses = ("todo", "inprogress", "done", "null", "string")


def statuses_markup(mode=None, statuses=statuses) -> ReplyKeyboardMarkup:
    # flexing on aiogram devs
    class ElegantReplyKeyboardBuilder(ReplyKeyboardBuilder):
        def __iadd__(self, other: KeyboardButton):
            self.add(other)

    builder = ElegantReplyKeyboardBuilder()
    for i in statuses:
        if mode == "tasks":
            builder += KeyboardButton(text=f"/tasks {i}", callback_data=i)
        else:
            builder += KeyboardButton(text=i, callback_data=i)

    builder.adjust(1)
    return builder.as_markup()


def mainmenu_markup(menupositions):
    builder = ReplyKeyboardBuilder()
    for i in menupositions:
        builder.add(KeyboardButton(text=f"/{i}", callback_data=i))
    builder.adjust(3)
    return builder.as_markup()


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    router = dp.include_router(Router())

    async def run_at(target_time, async_func, *args):
        now = datetime.datetime.now()
        delay = (target_time - now).total_seconds()

        if delay < 0:
            raise Exception("Чюююваккк. Запланировал на прошлое ЧЗХ??")

        await asyncio.sleep(delay)
        return await async_func(*args)

    async def reminder(chat_id):
        while chat_id in reminder_cooldown:
            today = datetime.datetime.now()

            today = today.replace(hour=23, minute=29, second=0)

            await run_at(
                today + datetime.timedelta(days=reminder_cooldown[chat_id]),
                lambda: bot.send_message(
                    chat_id=chat_id, text="Daily report: All systems normal"
                ),
            )

    @router.message(Command("togglereminder"))
    async def toggle_remind(message: Message):
        res = re.findall(
            pattern=r"^(?:/togglereminder)\s+(\d{1,10})$", string=message.text
        )
        if message.chat.id in reminder_cooldown.keys():
            reminder_cooldown.pop(message.chat.id)
            await message.answer("напоминалка убит")
        else:
            if bool(res):
                reminder_cooldown[message.chat.id] = int(res[0])
                await message.answer(f"установлена напоминалка каждые {res[0]} дней")
                asyncio.create_task(reminder(message.chat.id))
            else:
                await message.answer("неправильный формат")

    @router.message(Command("start"))
    async def start(message: Message):
        await message.answer(
            text="Охаё! 🖖",
            reply_markup=mainmenu_markup(
                ["greet", "tasks", "addtask", "deltask", "dayof", "togglereminder"]
            ),
        )
        r = requests.post(
            url=f"http://127.0.0.1:8000/api/tgrooms/?telegram_chat_id={message.chat.id}"
        )
        await message.answer(text=r.text)

    @router.message(Command("greet"))
    async def greet(message: Message):
        await message.answer("Если ты не гамасек, скажи приветик за 5 сек")
        var = datetime.datetime.now() + datetime.timedelta(seconds=5)
        await message.answer(f"приффетик в {var}")
        task = asyncio.create_task(
            run_at(
                var,
                lambda: bot.send_message(chat_id=message.chat.id, text="ПРИФФЕТИК 👋"),
            )
        )

        await task

    def get_room_id(chat_id: int) -> int:  # type: ignore
        r = requests.get(
            url="http://127.0.0.1:8000/api/tgrooms/",
            headers={"accept": "application/json"},
        )

        def room_for_current_tgchat(room):
            return room["tgchat"]["telegram_chat_id"] == chat_id

        rooms = list(
            room["id"] for room in r.json() if room and room_for_current_tgchat(room)
        )
        return int(rooms[0])

    @router.message(Command("tasks"))
    async def tasks(message: Message):
        # await message.answer(text=str(get_room_id(message.chat.id)))
        r = requests.get(
            url=f"http://127.0.0.1:8000/api/cards_for_specific_room/{get_room_id(message.chat.id)}",
            headers={"accept": "application/json"},
        )
        cards = r.json()["cards"]

        await message.answer(text=str(cards))

        def gen_message(status: str):
            filtered_tasks_string = ",\n".join(
                map(
                    lambda x: f"{x['id']}: {x['title']}",
                    filter(lambda k: k["status"] == status, cards),
                )
            )

            return f"Задачи {status}:\n {filtered_tasks_string}"

        if message.text == "/tasks":
            statuses_plus_all = ("all", *statuses)
            await message.answer(
                text="Кого хочешь выбирай: ",
                reply_markup=statuses_markup(mode="tasks", statuses=statuses_plus_all),
            )
        else:
            if message.text == "/tasks all":
                await message.answer(str(cards))
            else:
                for i in statuses:
                    if message.text == f"/tasks {i}":
                        if i == "null":
                            await message.answer(text=gen_message(""))
                        else:
                            await message.answer(text=gen_message(i))
            await message.answer(
                text="closing menu...", reply_markup=ReplyKeyboardRemove()
            )

    @router.message(Command("dayof"))
    async def dayof(message: Message):
        from langchain_gigachat.chat_models import GigaChat

        model = GigaChat(
            credentials=CREDENTIALS,
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
            verify_ssl_certs=False,
        )

        from langchain_core.messages import HumanMessage, SystemMessage

        day = datetime.datetime.now().day
        iso_week = datetime.datetime.now().isocalendar().week
        week = ceil(day / 7)
        month = datetime.datetime.now().month

        months = [
            "",
            "января",
            "февраля",
            "марта",
            "апреля",
            "мая",
            "июня",
            "июля",
            "августа",
            "сентября",
            "октября",
            "ноября",
            "декабря",
        ]

        month_cyrillic = months[month]
        messages = [
            SystemMessage(content=""),
            HumanMessage(
                content=f"какой праздник {day} {month_cyrillic} в России? ИЛИ {day} {month_cyrillic} - день чего? В этом году это {week} неделя {month_cyrillic} или {iso_week} в году. Сейчас 2025 год. Ни в коем случае не пробуй считать праздники по дням недели - ошибешься."
            ),
        ]

        output = model.invoke(messages)
        await message.answer(str(output.content))

    @router.message(Command("deltask"))
    async def delete_task(message: Message):
        res = re.findall(pattern=r"^(?:/deltask)\s+(\d+)$", string=message.text)

        if bool(res):
            requests.delete(url=f"http://127.0.0.1:8000/api/cards/{int(res[0])}")
            await message.answer(f"{int(res[0])} убит")
        else:
            await message.answer("неправильный формат")

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

                    await message.answer(
                        "Выслушал тебя, дорогой", reply_markup=ReplyKeyboardRemove()
                    )
                    data = await state.get_data()
                    print(data)

                    requests.post(
                        url="http://127.0.0.1:8000/api/cards",
                        headers={"accept": "application/json"},
                        json={
                            "title": data["title_description"].split("\n")[0],
                            "description": data["title_description"].split("\n")[1]
                            if "\n" in data["title_description"]
                            else "",
                            "room_id": get_room_id(message.chat.id),
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

    import aiohttp

    @router.inline_query()
    async def handle_inline_query(inline_query: InlineQuery):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://127.0.0.1:8000/api/cards",
                headers={"accept": "application/json"},
            ) as response:
                kanban = await response.json()

        cards = kanban.get("cards", [])

        results = [
            InlineQueryResultArticle(
                id=str(card_id),
                title=card["title"],
                description=card["description"],
                input_message_content=InputTextMessageContent(message_text=str(card)),
            )
            for card_id, card in enumerate(cards)
        ]

        await bot.answer_inline_query(
            inline_query_id=inline_query.id, results=results, cache_time=1
        )

    def register_callback(
        action: str, handler: Callable[[CallbackQuery], Awaitable[None]]
    ) -> None:
        async def wrapper(query: CallbackQuery) -> None:
            print(f"Handling action: {action}")
            await handler(query)

        router.callback_query.register(wrapper, F.data == action)

    # register_callback("register", lambda q: send_register(q.message))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
