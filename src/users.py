import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from db import DBDriver
from src.app import dp


class UserInput(StatesGroup):
    first_name = State()
    last_name = State()
    patronymic_name = State()
    email = State()
    tg_id = State()
    cmd_cancel = State()


def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(user_input_start, commands="registration", state="*")
    dp.register_message_handler(user_input_first_name, state=UserInput.first_name)
    dp.register_message_handler(user_input_last_name, state=UserInput.last_name)
    dp.register_message_handler(user_input_patronymic_name, state=UserInput.patronymic_name)
    dp.register_message_handler(user_input_email, state=UserInput.email)
    dp.register_message_handler(cmd_cancel, state=UserInput.cmd_cancel)
    dp.register_message_handler(cmd_cancel, Text(equals="Отмена", ignore_case=True), state="*")


@dp.message_handler(lambda message: message.text == "Зарегистрироваться")
async def user_input_start(message: types.Message):
    await UserInput.first_name.set()
    await message.answer("Введите ваше ИМЯ: ")


async def user_input_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await UserInput.next()
    await message.reply("Введите вашу ФАМИЛИЮ: ")


async def user_input_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await UserInput.next()
    await message.answer("Введите ваше ОТЧЕСТВО: ")


async def user_input_patronymic_name(message: types.Message, state: FSMContext):
    await state.update_data(patronymic_name=message.text)
    await UserInput.next()
    await message.answer("Введите ваш e-mail: ")


async def user_input_email(message: types.Message, state: FSMContext):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, message.text) is None:
        await message.answer("Пожалуйста, напишите e-mail в формате user@example.com")
        return
    await state.update_data(email=message.text)
    await state.update_data(tg_id=message.from_user.id)
    user_data = await state.get_data()
    user_db_object = DBDriver()
    user_db_object.add_user(user_data)
    await state.finish()


async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Действие отменено", reply_markup=types.ReplyKeyboardRemove())
