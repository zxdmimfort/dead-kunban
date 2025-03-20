import asyncio
from datetime import datetime as dt, timedelta
import json
from math import ceil
import sys
from typing import Any
from aiogram import Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

import requests  # type: ignore

from aiogram.types import ReplyKeyboardRemove
import re

from add_task import router as add_task_router
from task_actions import router as task_actions_router

from init import bot, API_HOST, statuses, CREDENTIALS
from markups import just_markup, mainmenu_markup
import crud_ops


from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage

import utils

admins: tuple[str, ...] = ("aoi_dev", "mimfort")
active_notification_tasks: dict[int, asyncio.Task[Any]] = {}
g_countdown: dict[int, bool] = {}
g_sleep: dict[int, int] = {}


async def main() -> None:
    dp = Dispatcher()
    router = dp.include_router(Router())
    dp.include_router(add_task_router)
    dp.include_router(task_actions_router)

    async def run_at_with_countdown(sleep_time: float, target_time: dt):
        while True:
            now = dt.now()
            left = target_time - now
            delay = left.total_seconds()
            days, hours, minutes, seconds = utils.timedelta_converter(
                left.total_seconds()
            )
            yield f"{days} дней {hours} часов {minutes} минут {seconds} секунд"

            if delay <= sleep_time:
                break
            await asyncio.sleep(sleep_time)

    def text_to_emoji(model, text):
        messages = [
            SystemMessage(content="Переведи следующую фразу на язык emoji:"),
            HumanMessage(content=f"{text}"),
        ]

        def is_emoji(character):
            code_point = ord(character)
            emoji_ranges = [
                (0x1F600, 0x1F64F),  # Emoticons
                (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
                (0x1F680, 0x1F6FF),  # Transport and Map Symbols
                (0x2600, 0x26FF),  # Miscellaneous Symbols
                (0x2700, 0x27BF),  # Dingbats
                (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
                (0x1F1E6, 0x1F1FF),  # Regional Indicator Symbols (flags)
                (0x1F400, 0x1F4FF),  # Animals, Nature, and Objects
            ]
            return any(start <= code_point <= end for start, end in emoji_ranges)

        output = model.invoke(messages)
        return (
            output.content
            if output.response_metadata["finish_reason"] == "stop"
            and all(map(is_emoji, list(output.content)))
            else ""
        )

    async def notify_todo(chat_id):
        tasks_for_notification = crud_ops.tasks_for_notification(chat_id)
        if tasks_for_notification:
            model = GigaChat(
                credentials=CREDENTIALS,
                scope="GIGACHAT_API_PERS",
                model="GigaChat",
                verify_ssl_certs=False,
            )

            message_construct = [
                f"""<i>{task["title"]}</i> {text_to_emoji(model, task["title"])}
{"\n" + task["description"] if task["description"] else ""} """
                for task in tasks_for_notification
            ]

            await bot.send_message(
                chat_id=chat_id,
                text="<b>todo:</b>\n" + "\n".join(message_construct),
                parse_mode="HTML",
            )
        else:
            await bot.send_message(chat_id=chat_id, text=str("На сегодня дел нет!"))

    async def notify_done(chat_id):
        tasks = crud_ops.tasks_for_specific_chat(chat_id)
        model = GigaChat(
            credentials=CREDENTIALS,
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
            verify_ssl_certs=False,
        )

        message_construct = []
        for task in tasks:
            if task["status"] == "done" and task["period"] != -1:
                days, hours, minutes, seconds = utils.timedelta_converter(
                    json.loads(task["till_todo"])["total_seconds"]
                )

                m = f"""<i>{task["title"]}</i> {text_to_emoji(model, task["title"])}{"\n" + task["description"] if task["description"] else ""}
Отсчёт до статуса todo: {days} дней {hours} часов {minutes} минут {seconds} секунд"""

                message_construct.append(m)
        await bot.send_message(
            chat_id=chat_id,
            text="<b>done:</b>\n" + "\n".join(message_construct),
            parse_mode="HTML",
        )

    @router.message(Command("notify", "уведомить"))
    async def notify_now(message: Message):
        await notify_todo(message.chat.id)

    @router.message(Command("notify_full", "уведомить_все"))
    async def notify_full(message: Message):
        await notify_todo(message.chat.id)
        await notify_done(message.chat.id)

    async def reminder(chat_id):
        r = crud_ops.get_telegram_room(chat_id)
        preferred_notification_times: list[dict[str, str]] = r[
            "preferred_notification_times"
        ]
        sent_messages = []
        while True:
            customdate = dt.today().date()
            customtime = [
                dt.strptime(t["time"], "%H:%M:%S").time()
                for t in preferred_notification_times
            ]
            dateplustime = [dt.combine(customdate, t) for t in customtime]

            sorted_dateplustime = sorted(
                [
                    dtobj + timedelta(days=1) if dtobj < dt.now() else dtobj
                    for dtobj in dateplustime
                ],
                key=lambda t: (t - dt.now()).total_seconds(),
            )

            target_time = sorted_dateplustime[0]
            async for countdown in run_at_with_countdown(g_sleep[chat_id], target_time):
                if g_countdown[chat_id]:
                    sent_messages.append(
                        await bot.send_message(
                            chat_id=chat_id, text=f"До напоминалки: {countdown}"
                        )
                    )
                    for i in sent_messages[:-1]:
                        if await utils.auto_remove_message(i):
                            sent_messages.remove(i)

            await notify_todo(chat_id)
            await asyncio.sleep(g_sleep[chat_id] + 1)

    @router.message(Command("toggle_countdown", "переключить_отсчет"))
    async def toggle_countdown(message: Message):
        chat_id = message.chat.id

        if chat_id in g_countdown.keys():
            g_countdown[chat_id] = not g_countdown[chat_id]
        else:
            g_countdown[chat_id] = False
        await message.answer(f"Отсчёт: {'on' if g_countdown[chat_id] else 'off'}")

    @router.message(Command("set_countdown_sleep_value", "сон"))
    async def set_countdown_sleep_value(message: Message):
        regex = re.match(  # type: ignore
            pattern=r"(?P<command>/[\wа-яА-Я]+)(?P<bot_name>@\w+)?\s+(?P<sleep_sec>\d{1,5})",
            string=message.text,
        )
        if regex is None:
            return
        sleep_in_seconds = int(regex["sleep_sec"])
        assert sleep_in_seconds < 60 * 60 * 24
        g_sleep[message.chat.id] = sleep_in_seconds
        await message.answer(f"Sleep is set to be {sleep_in_seconds} secs")

        active_notification_tasks[message.chat.id].cancel()
        active_notification_tasks[message.chat.id] = asyncio.create_task(
            reminder(message.chat.id)
        )

    @router.message(
        Command("set_preferred_notification_time", "установить_время_уведомления")
    )
    async def set_preferred_notification_time(message: Message):
        regex = re.match(  # type: ignore
            pattern=r"(?P<command>/\w+)(?P<bot_name>@\w+)?\s+(?P<notification_times>(?:\d{2}\:\d{2}\:\d{2}[,;\s]*)+)",
            string=message.text,
        )
        if regex is None:
            return

        split_times = re.split(r"[,;\s]+", regex.group("notification_times"))

        assert all(map(lambda t: dt.strptime(t, "%H:%M:%S").time(), split_times))

        split_times_set = set(split_times)
        new_notification_times = [{"time": time} for time in split_times_set]
        old_notification_times = crud_ops.get_telegram_room(message.chat.id)[
            "preferred_notification_times"
        ]

        requests.put(
            url=f"http://{API_HOST}/api/set_preferred_notification_time?telegram_chat_id={message.chat.id}",
            headers={"accept": "application/json"},
            json=new_notification_times,
        )

        await message.answer(
            text=f"{utils.times_format_func(old_notification_times)} -> {utils.times_format_func(new_notification_times)}"
        )
        active_notification_tasks[message.chat.id].cancel()
        active_notification_tasks[message.chat.id] = asyncio.create_task(
            reminder(message.chat.id)
        )

    def activate_reminders_on_start():
        with open("reminder_chat_ids.json", "r", encoding="utf-8") as file:
            chat_ids = json.load(file)
            for chat_id in chat_ids:
                task = asyncio.create_task(reminder(chat_id))
                active_notification_tasks[chat_id] = task
                g_countdown[chat_id] = False
                g_sleep[chat_id] = 5

    activate_reminders_on_start()

    @router.message(Command("toggle_reminder", "переключить_уведомления"))
    async def toggle_remind(message: Message):
        notify = crud_ops.get_telegram_room(message.chat.id)["notify"]
        preferred_notification_times = crud_ops.get_telegram_room(message.chat.id)[
            "preferred_notification_times"
        ]
        crud_ops.put_room_notifications(
            telegram_chat_id=int(message.chat.id), turned_on=not notify
        )
        notify = not notify  # toggling

        if not notify:  #  if notify is false
            await message.answer("напоминалка убит")
            if message.chat.id in active_notification_tasks.keys():
                active_notification_tasks[message.chat.id].cancel()
                active_notification_tasks.pop(message.chat.id)
        else:
            await message.answer(
                f"установлена напоминалка на {utils.times_format_func(preferred_notification_times)}"
            )
            active_notification_tasks[message.chat.id] = asyncio.create_task(
                reminder(message.chat.id)
            )
            g_countdown[message.chat.id] = False
            g_sleep[message.chat.id] = 5

    @router.message(Command("start"))
    async def start(message: Message):
        await message.answer(text=str(message.chat.id))
        await message.answer(
            text="Охаё! 🖖",
            reply_markup=mainmenu_markup(
                [
                    "notify",
                    "tasks",
                    "addtask",
                    "edit",
                    "toggle_reminder",
                    "toggle_countdown",
                    "dayof",
                ]
            ),
        )

    @router.message(Command("tasks", "задачи"))
    @utils.autoremove_message(5)
    async def tasks(message: Message):
        tasks = crud_ops.tasks_for_specific_chat(message.chat.id)
        match = re.match(
            pattern=r"(?P<command>/[\wа-яА-Я]+)(?P<bot_name>@\w+)?\s+(?P<status>(all|todo|done))",
            string=message.text,
        )
        if not match:
            statuses_plus_all = ("all", *statuses)
            return await message.answer(
                text="Кого хочешь выбирай: ",
                reply_markup=just_markup(mode="tasks", statuses=statuses_plus_all),
            )
        else:
            if match.group("status") == "all":
                for t in tasks:
                    await message.answer(text=t["beautiful_card"])
            else:
                await message.answer(text=match.group("status"))
                for t in tasks:
                    if t["status"] == match.group("status"):
                        await message.answer(text=t["beautiful_card"])
                return await message.answer(
                    text="closing menu...", reply_markup=ReplyKeyboardRemove()
                )

    @router.message(Command("dayof", "день_чего"))
    async def dayof(message: Message):
        model = GigaChat(
            credentials=CREDENTIALS,
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
            verify_ssl_certs=False,
        )
        day = dt.now().day
        iso_week = dt.now().isocalendar().week
        week = ceil(day / 7)
        current_month = dt.now().month - 1
        year = dt.now().year
        months = [
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
        month_cyrillic = months[current_month]
        messages = [
            SystemMessage(content=""),
            HumanMessage(
                content=f"Что отмечают {day} {month_cyrillic} в России? Если в этом году ({year}) это {week} неделя {month_cyrillic}({iso_week} неделя в году)."
            ),
        ]
        output = model.invoke(messages)
        await message.answer(str(output.content))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":

    def handle_sigint():
        with open("reminder_chat_ids.json", "w", encoding="utf-8") as file:
            json.dump(
                list(active_notification_tasks.keys()),
                file,
                ensure_ascii=False,
                indent=4,
            )
        sys.exit(0)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Received exit, exiting")
    finally:
        handle_sigint()
