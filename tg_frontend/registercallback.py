from aiogram.types import CallbackQuery
from typing import Callable, Awaitable
from aiogram import F, Router
from aiogram.fsm.context import FSMContext


def register_callback(
    router: Router,
    action: str,
    handler: Callable[[CallbackQuery, FSMContext], Awaitable[None]],
) -> None:
    async def wrapper(query: CallbackQuery, state: FSMContext) -> None:
        print(f"Handling action: {action}")
        await handler(query, state)  # Pass FSMContext to the handler

    router.callback_query.register(wrapper, F.data.startswith(action))
