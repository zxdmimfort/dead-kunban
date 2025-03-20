from init import statuses
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def just_markup(mode="", statuses=statuses) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for i in statuses:
        builder.add(
            KeyboardButton(text=f"/{mode} {i}" if mode else f"{i}", callback_data=i)
        )

    builder.adjust(1)
    return builder.as_markup()


def mainmenu_markup(menupositions):
    builder = ReplyKeyboardBuilder()
    for i in menupositions:
        builder.add(KeyboardButton(text=f"/{i}", callback_data=i))
    builder.adjust(3)
    return builder.as_markup()


def tasks_markup(tasks_json, prefix="tasks_selection") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for task in tasks_json:
        builder.add(
            InlineKeyboardButton(
                text=f"{task['id']}: {task['title']}; {task['description']}; period: {task['period']}; {task['status']}",
                callback_data=f"{prefix}:{task['id']}",
            )
        )

    builder.adjust(1)
    return builder.as_markup()
