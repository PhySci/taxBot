import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db import DBDriver


class UserInput(StatesGroup):
    first_name = State()
    last_name = State()
    patronymic_name = State()
    email = State()
    tg_id = State()


async def cmd_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Зарегистрироваться", callback_data='registration'),
        types.InlineKeyboardButton(text="Доп. информация", callback_data='add_info'),
    ]
    keyboard.add(*buttons)
    await message.answer("Добро полажловать в TaxBot!"
                         " Нажмите кнопку или введите команду"
                         " (посмотреть можно введя /help) ",
                         reply_markup=keyboard)


async def user_input_start(message: types.Message):
    await UserInput.first_name.set()
    await message.answer("Введите ваше ИМЯ: ")


async def user_input_first_name(message: types.Message, state: FSMContext):
    pattern = r"^[A-ЯЁа-яёA-Za-z]+$"
    if re.match(pattern, message.text) is None:
        await message.answer("Пожалуйста, введите строку, состоящую из букв")
        return
    await state.update_data(first_name=message.text.capitalize())
    await UserInput.next()
    await message.answer("Введите вашу ФАМИЛИЮ: ")


async def user_input_last_name(message: types.Message, state: FSMContext):
    pattern = r"^[A-ЯЁа-яёA-Za-z]+$"
    if re.match(pattern, message.text) is None:
        await message.answer("Пожалуйста, введите строку, состоящую из букв")
        return
    await state.update_data(last_name=message.text.capitalize())
    await UserInput.next()
    await message.answer("Введите ваше ОТЧЕСТВО: ")


async def user_input_patronymic_name(message: types.Message, state: FSMContext):
    pattern = r"^[A-ЯЁа-яёA-Za-z]+$"
    if re.match(pattern, message.text) is None:
        await message.answer("Пожалуйста, введите строку, состоящую из букв")
        return
    await state.update_data(patronymic_name=message.text.capitalize())
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
    # user_db_object = DBDriver()
    # user_db_object.add_user(user_data)
    await state.finish()


async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.reply("Нечего отменять")
    else:
        await state.finish()
        await message.reply("Действие отменено")


async def catch_other_message(message: types.Message):
    await message.reply("Неизвестный тип сообщений. Воспользуйся командой /help")


async def additional_info(message: types.Message):
    await message.reply("Тут будет дополнительная информация")


async def get_help_command(message: types.Message):
    await message.reply(
        "* Чтобы зарегистрироваться, введите команду /registration\n"
        "* Чтобы получить дополнительную информацию, введите команду /add_info\n"
        "* Чтобы отменить ввод, введите команду /cancel или напишите 'отмена'\n"
    )


async def catch_receipt(message: types.Message):
    print(message)
    driver = DBDriver()
    driver.add_receipt(message)
    await message.answer("Чек принят!")


# @dp.message_handler(lambda message: message.text == "Выключить бот", commands="stop")
# async def stop(message: types.Message):
#     await on_shutdown()
#     await message.reply("Бот остановлен")
