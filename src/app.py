import logging
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, ParseMode
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import text, bold
from settings import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_HOST, WEBAPP_HOST, WEBAPP_PORT, LOCAL_DEV
from utils import setup_logging
from db import DBDriver

import locale

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

from aiogram import Bot, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

_logger = logging.getLogger(__name__)


def init_bot():
    """
    """
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())
    return bot, dp

bot, dp = init_bot()


async def on_startup(dp):
    _logger.warning('Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dp):
    _logger.warning('Bye! Shutting down webhook connection')
    bot.close()


@dp.message_handler(regexp='https:\/\/lknpd.nalog.ru/api/v1/receipt/\d+/[\w]+/print')
async def catch_receipt(message: Message):
    print(message)
    driver = DBDriver()
    driver.add_recept(message)
    await message.answer("Чек принят!")
    pass


@dp.message_handler()
async def catch_other_message(message: Message):
    await message.answer("Неизвестный тип сообщений")


def main():
    setup_logging()

    if LOCAL_DEV:
        print("LOCAL development mode!")
        executor.start_polling(dp, skip_updates=True)
    else:
        print('Non local run')
        print(WEBHOOK_URL)
        print(WEBHOOK_PATH)
        print(WEBAPP_HOST)
        print(WEBAPP_PORT)
        start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, skip_updates=True,
                      on_startup=on_startup, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == '__main__':
    main()
