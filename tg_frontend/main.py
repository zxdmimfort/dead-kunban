import asyncio
import datetime
from math import ceil
from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from typing import Callable, Awaitable

import requests  # type: ignore

from aiogram.types import ReplyKeyboardRemove
import re
from add_task import router as add_task_router
from task_actions import router as task_actions_router

from init import bot, API_HOST, statuses, CREDENTIALS
from markups import statuses_markup, mainmenu_markup
from crud_ops import delete_task_by_id, retrieve_room_id


admins: tuple[str, ...] = ("aoi_dev", "mimfort")
reminder_cooldown: dict[int, int] = {}


async def main() -> None:
    dp = Dispatcher()
    router = dp.include_router(Router())
    dp.include_router(add_task_router)
    dp.include_router(task_actions_router)

    async def run_at(target_time, async_func, *args):
        now = datetime.datetime.now()
        delay = (target_time - now).total_seconds()

        if delay < 0:
            raise Exception("Чюююваккк. Как ты запланировал на прошлое ЧЗХ??")

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
        await message.answer(text=str(message.chat.id))
        await message.answer(
            text="Охаё! 🖖",
            reply_markup=mainmenu_markup(
                ["greet", "tasks", "addtask", "deltask", "dayof", "togglereminder"]
            ),
        )

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

    @router.message(Command("tasks"))
    async def tasks(message: Message):
        # await message.answer(text=str(get_room_id(message.chat.id)))
        r = requests.get(
            url=f"http://{API_HOST}/api/cards_for_specific_room/{retrieve_room_id(message.chat.id)}",
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
            await message.answer(f"{delete_task_by_id(int(res[0]))} убит")
        else:
            await message.answer("неправильный формат")

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
