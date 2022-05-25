import logging

from aiogram.types import Message, BotCommand
from settings import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_HOST, WEBAPP_HOST, WEBAPP_PORT, LOCAL_DEV
from utils import setup_logging
from db import DBDriver

from users import register_handlers_user

import locale

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

from aiogram import Bot, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils.executor import start_webhook

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


@dp.message_handler(regexp="https:\/\/lknpd.nalog.ru/api/v1/receipt/\d+/[\w]+/print")
async def catch_receipt(message: Message):
    print(message)
    driver = DBDriver()
    driver.add_receipt(message)
    await message.answer("Чек принят!")
    pass


@dp.message_handler()
async def catch_other_message(message: Message):
    await message.answer("Неизвестный тип сообщений. Воспользуйся командой /help")


@dp.message_handler(lambda message: message.text == "Доп. информация", command="additional_info")
async def additional_info(message: types.Message):
    await message.reply("Тут будет дополнительная информация")


@dp.message_handler(lambda message: message.text == "Выключить бот", commands="stop")
async def stop(message: types.Message):
    await on_shutdown()
    await message.reply("Бот остановлен")


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    buttons = ["Зарегистрироваться", "Доп. информация", "Выключить бот"]
    keyboard.add(*buttons)
    await message.answer("Добро полажловать в TaxBot!", reply_markup=keyboard)


@dp.message_handler(commands="help")
async def get_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь")


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
        await set_commands(bot)
        register_handlers_user(dp)
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
