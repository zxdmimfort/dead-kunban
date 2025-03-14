from init import statuses
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def statuses_markup(mode="", statuses=statuses) -> ReplyKeyboardMarkup:
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
