import asyncio
from functools import wraps
from init import bot


def times_format_func(times: list[dict[str, str]]) -> str:
    return ", ".join([t["time"] for t in times])


def timedelta_converter(total_seconds) -> tuple[int, ...]:
    delay = total_seconds
    days = int(delay // 84000)
    hours = int((delay % 84000) // 3600)  # Total number of hours
    minutes = int(((delay % 84000) % 3600) // 60)  # Minutes within the last hour
    seconds = int(delay % 60)  # Remaining seconds

    return days, hours, minutes, seconds


async def auto_remove_markup(sent_message, after_sec=0):
    await asyncio.sleep(after_sec)
    try:
        await bot.edit_message_reply_markup(
            chat_id=sent_message.chat.id,
            message_id=sent_message.message_id,
            reply_markup=None,
        )
        return True
    except Exception as e:
        print(f"Error deleting markup: {e}")
        return False


async def auto_remove_message(sent_message, after_sec=0) -> bool:
    await asyncio.sleep(after_sec)
    try:
        await bot.delete_message(
            chat_id=sent_message.chat.id, message_id=sent_message.message_id
        )
        return True
    except Exception as e:
        print(f"Error deleting message: {e}")
        return False


def autoremove_message(after_sec=10):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def _remove_message(sent_message, after_sec):
                await asyncio.sleep(after_sec)
                try:
                    await bot.delete_message(
                        chat_id=sent_message.chat.id, message_id=sent_message.message_id
                    )
                except Exception as e:
                    print(f"Error deleting message: {e}")

            sent_message = await func(*args, **kwargs)
            asyncio.create_task(_remove_message(sent_message, after_sec))
            return sent_message

        return wrapper

    return decorator


def autoremove_markup(after_sec=10):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def _remove_markup(sent_message, after_sec):
                await asyncio.sleep(after_sec)
                await bot.edit_message_reply_markup(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    reply_markup=None,
                )

            sent_message = await func(*args, **kwargs)
            asyncio.create_task(_remove_markup(sent_message, after_sec))
            return sent_message

        return wrapper

    return decorator
