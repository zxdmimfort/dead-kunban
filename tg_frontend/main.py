import asyncio
import datetime
from datetime import datetime as dt
from math import ceil
from aiogram import Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

import requests  # type: ignore

from aiogram.types import ReplyKeyboardRemove
import re
from add_task import router as add_task_router
from task_actions import router as task_actions_router

from init import bot, API_HOST, statuses, CREDENTIALS
from markups import statuses_markup, mainmenu_markup
import crud_ops

admins: tuple[str, ...] = ("aoi_dev", "mimfort")


async def main() -> None:
    dp = Dispatcher()
    router = dp.include_router(Router())
    dp.include_router(add_task_router)
    dp.include_router(task_actions_router)

    async def run_at(target_time, async_func, *args):
        now = dt.now()
        delay = (target_time - now).total_seconds()

        if delay < 0:
            raise Exception("Чюююваккк. Как ты запланировал на прошлое ЧЗХ??")

        await asyncio.sleep(delay)
        return await async_func(*args)

    async def run_at_with_countdown(sleep_time, target_time, async_func, *args):
        while True:
            now = dt.now()
            delay = (target_time - now).total_seconds()
            if delay < 0:
                raise Exception("Чюююваккк. Как ты запланировал на прошлое ЧЗХ??")
            yield f"До напоминалки: {delay / 3600} часов {delay % 3600 / 60} минут {delay % 3600 % 60} секунд"
            if delay <= 1:
                break
            await asyncio.sleep(sleep_time)
        await async_func(*args)

    async def notify(chat_id):
        tasks_for_notification = crud_ops.tasks_for_notification(chat_id)
        if tasks_for_notification:
            await bot.send_message(chat_id=chat_id, text=str(tasks_for_notification))
        else:
            await bot.send_message(chat_id=chat_id, text=str("На сегодня дел нет!"))

    @router.message(Command("notify"))
    async def notify_now(message: Message):
        await message.answer(f"{message.chat.id}")
        await notify(message.chat.id)

    async def reminder(chat_id):
        r = crud_ops.get_telegram_room(chat_id)
        preffered_notification_time = r["preferred_notification_time"]

        while crud_ops.must_notify(chat_id):
            await bot.send_message(
                chat_id=chat_id, text=str(crud_ops.must_notify(chat_id))
            )

            customdate = dt.today().date()
            customtime = dt.strptime(preffered_notification_time, "%H:%M:%S").time()
            dateplustime = dt.combine(customdate, customtime)
            add = (
                datetime.timedelta(days=1)
                if (dateplustime - dt.now()).total_seconds() < 0
                else datetime.timedelta(days=0)
            )

            async for countdown in run_at_with_countdown(
                sleep_time=30,
                target_time=dateplustime + add,
                async_func=lambda: notify(chat_id),
            ):
                await bot.send_message(chat_id=chat_id, text=countdown)
                preffered_notification_time = r["preferred_notification_time"]
                new_notification_time = r["preferred_notification_time"]

                if new_notification_time != preffered_notification_time:
                    break
                    # if crud_ops.must_notify(chat_id):

    @router.message(Command("set_preferred_notification_time"))
    async def set_preferred_notification_time(message: Message):
        regex = re.match(  # type: ignore
            pattern=r"/set_preferred_notification_time\s+(?P<notification_time>\d\d\:\d\d\:\d\d)",
            string=message.text,
        )
        if regex is None:
            return
        new_notification_time = regex.group("notification_time")
        old_notification_time = crud_ops.get_telegram_room(message.chat.id)[
            "preferred_notification_time"
        ]
        requests.put(
            url=f"http://{API_HOST}/api/set_preferred_notification_time?telegram_chat_id={message.chat.id}&preferred_notification_time={new_notification_time}"
        )
        await message.answer(text=f"{old_notification_time} -> {new_notification_time}")

    @router.message(Command("togglereminder"))
    async def toggle_remind(message: Message):
        notify = crud_ops.get_telegram_room(message.chat.id)["notify"]
        preferred_notification_time = crud_ops.get_telegram_room(message.chat.id)[
            "preferred_notification_time"
        ]
        crud_ops.put_room_notifications(
            telegram_chat_id=int(message.chat.id), turned_on=not notify
        )
        notify = not notify
        if not notify:
            await message.answer("напоминалка убит")
        else:
            await message.answer(
                f"установлена напоминалка на {preferred_notification_time}"
            )
            await reminder(message.chat.id)

    @router.message(Command("start"))
    async def start(message: Message):
        await message.answer(text=str(message.chat.id))
        await message.answer(
            text="Охаё! 🖖",
            reply_markup=mainmenu_markup(
                ["tasks", "addtask", "edit", "dayof", "togglereminder"]
            ),
        )

    @router.message(Command("tasks"))
    async def tasks(message: Message):
        # await message.answer(text=str(get_room_id(message.chat.id)))
        tasks = requests.get(
            url=f"http://{API_HOST}/api/cards_for_specific_room?room_id={crud_ops.retrieve_room_id(message.chat.id)}",
            headers={"accept": "application/json"},
        ).json()["cards"]

        await message.answer(text=str(tasks))

        def gen_message(status: str):
            filtered_tasks_string = ",\n".join(
                map(
                    lambda x: f"{x['id']}: {x['title']}",
                    filter(lambda k: k["status"] == status, tasks),
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
                await message.answer(str(tasks))
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

        day = dt.now().day
        iso_week = dt.now().isocalendar().week
        week = ceil(day / 7)
        month = dt.now().month

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

    # @router.message(Command("deltask"))
    # async def delete_task(message: Message):
    #     res = re.findall(pattern=r"^(?:/deltask)\s+(\d+)$", string=message.text)

    #     if bool(res):
    #         await message.answer(f"{crud_ops.delete_task_by_id(int(res[0]))} убит")
    #     else:
    #         await message.answer("неправильный формат")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
