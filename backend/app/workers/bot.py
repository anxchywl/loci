import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.core.config import get_settings

logger = logging.getLogger(__name__)

dispatcher = Dispatcher()


@dispatcher.message(CommandStart())
async def handle_start(message: Message) -> None:
    settings = get_settings()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Open Loci",
                    web_app=WebAppInfo(url=settings.telegram_mini_app_url),
                )
            ]
        ]
    )
    await message.answer("Pin your life moments to the map.", reply_markup=keyboard)


async def main() -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN must be set to run the bot")
    if not settings.telegram_mini_app_url:
        raise RuntimeError("TELEGRAM_MINI_APP_URL must be set to run the bot")

    logging.basicConfig(level=settings.log_level)
    bot = Bot(token=settings.telegram_bot_token)
    logger.info("bot polling started")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
