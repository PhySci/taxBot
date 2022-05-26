import locale
import logging
import handlers

from aiogram import Bot, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher.filters import Text
from aiogram.types import BotCommand
from settings import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_HOST, WEBAPP_HOST, WEBAPP_PORT, LOCAL_DEV
from utils import setup_logging

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

_logger = logging.getLogger(__name__)


def init_bot():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())
    return bot, dp


bot, dp = init_bot()


async def on_startup():
    _logger.warning("Starting connection")
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown():
    _logger.warning("Bye! Shutting down webhook connection")
    await bot.close()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/registration", description="Зарегистрироваться"),
        BotCommand(command="/additional_info", description="Доп. информация"),
        BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


def main():
    setup_logging()
    if LOCAL_DEV:
        print("LOCAL development mode!")
        set_commands(bot)

        dp.register_message_handler(handlers.cmd_start, commands="start")
        dp.register_message_handler(handlers.catch_other_message)
        dp.register_message_handler(handlers.additional_info, lambda message: message.text == "Доп. информация")
        dp.register_message_handler(handlers.additional_info, command="additional_info")
        dp.register_message_handler(handlers.get_help_command, commands="help")
        dp.register_message_handler(handlers.catch_receipt, regexp="https:\/\/lknpd.nalog.ru/api/v1/receipt/\d+/[\w]+/print")

        dp.register_message_handler(handlers.user_input_start, lambda message: message.text == "Зарегистрироваться")
        dp.register_message_handler(handlers.user_input_start, commands="registration", state="*")
        dp.register_message_handler(handlers.user_input_first_name, state=handlers.UserInput.first_name)
        dp.register_message_handler(handlers.user_input_last_name, state=handlers.UserInput.last_name)
        dp.register_message_handler(handlers.user_input_patronymic_name, state=handlers.UserInput.patronymic_name)
        dp.register_message_handler(handlers.user_input_email, state=handlers.UserInput.email)
        dp.register_message_handler(handlers.cmd_cancel, state=handlers.UserInput.cmd_cancel)
        dp.register_message_handler(handlers.cmd_cancel, Text(equals="Отмена", ignore_case=True), state="*")
        dp.register_message_handler(handlers.cmd_cancel, commands="cancel")

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
