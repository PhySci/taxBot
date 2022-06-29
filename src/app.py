import locale
import logging
import handlers

import aiogram
from aiogram.types import BotCommand
from aiogram import Bot, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher.filters import Text

from settings import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_HOST, WEBAPP_HOST, WEBAPP_PORT, LOCAL_DEV
from utils import setup_logging

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

_logger = logging.getLogger(__name__)
logging.getLogger("aiogram").setLevel(logging.INFO)


def init_bot():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.middleware.setup(LoggingMiddleware())
    return bot, dp


bot, dp = init_bot()


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "Запуск"),
        BotCommand("help", "Помощь"),
        BotCommand("registration", "Зарегистрироваться"),
        BotCommand("add_info", "Доп. информация"),
        BotCommand("cancel", "Отменить текущее действие")
    ])


async def on_startup():
    _logger.warning("Starting connection")
    await set_default_commands(dp)
    if not LOCAL_DEV:
        await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown():
    _logger.warning("Bye! Shutting down webhook connection")
    await bot.close()

commands_list = [
    "start",
    "registration",
    "help",
    "add_info",
    "cancel"
]


def main():
    setup_logging()

    dp.register_message_handler(handlers.cmd_start, commands="start")
    dp.register_message_handler(handlers.additional_info, commands="add_info")
    dp.register_message_handler(handlers.get_help_command, commands="help")

    dp.register_message_handler(
        handlers.catch_receipt,
        regexp="https:\/\/lknpd.nalog.ru/api/v1/receipt/\d+/[\w]+/print"
    )
    dp.register_message_handler(handlers.set_state_email_for_sending, commands="add_subscriber")
    dp.register_message_handler(handlers.add_email_for_sending, state=handlers.SendingMail.email)

    dp.register_callback_query_handler(
        handlers.from_button,
        handlers.instance.filter(action=["registrate", "info", "cancel", "add_info"]), state="*")

    dp.register_message_handler(handlers.cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
    dp.register_message_handler(handlers.cmd_cancel, Text(equals="/cancel", ignore_case=True), state="*")

    dp.register_message_handler(handlers.user_input_start, commands="registration", state="*")
    dp.register_message_handler(handlers.user_input_first_name, state=handlers.UserInput.first_name)
    dp.register_message_handler(handlers.user_input_patronymic_name, state=handlers.UserInput.patronymic_name)
    dp.register_message_handler(handlers.user_input_last_name, state=handlers.UserInput.last_name)
    dp.register_message_handler(handlers.user_input_email, state=handlers.UserInput.email)

    dp.register_message_handler(
        handlers.catch_other_message,
        content_types=["text", "sticker", "pinned_message", "photo", "audio"]
    )

    if LOCAL_DEV:
        print("Enabled local mode")
        executor.start_polling(dp, skip_updates=True)
    else:
        print("Enabled non local mode")
        print(WEBHOOK_URL)
        print(WEBHOOK_PATH)
        print(WEBAPP_HOST)
        print(WEBAPP_PORT)
        start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, skip_updates=True,
                      on_startup=on_startup, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == '__main__':
    main()
