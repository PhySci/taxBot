import os
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

from db import (
    DBDriver, STATUS_OK, STATUS_FAIL, STATUS_RECEIPT_ALREADY_EXIST,
    STATUS_USER_ALREADY_EXIST, STATUS_RECEIPT_UNKNOWN_USER, STATUS_MAIL_ALREADY_EXIST
)
from src.mailing import json_to_excel, send_email


class UserInput(StatesGroup):
    first_name = State()
    patronymic_name = State()
    last_name = State()
    email = State()
    tg_id = State()


class SendingMail(StatesGroup):
    email = State()


instance = CallbackData("button", "action")


def get_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text="Зарегистрироваться", callback_data=instance.new(action="registrate")),
        types.InlineKeyboardButton(text="Доп. информация", callback_data=instance.new(action="info")),
        types.InlineKeyboardButton(text="Отменить регистрацию", callback_data=instance.new(action="cancel")),
    ]
    keyboard.add(*buttons)
    return keyboard


async def cmd_start(message: types.Message):
    await message.answer("Добро полажловать в TaxBot!"
                         " Нажмите кнопку или введите команду"
                         " (посмотреть можно введя /help) ",
                         reply_markup=get_keyboard())


async def from_button(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data["action"] == "registrate":
        await UserInput.first_name.set()
        await call.message.answer("Введите ваше ИМЯ: ")

    elif callback_data["action"] == "info":
        await call.message.answer("Тут будет дополнительная информация")

    elif callback_data["action"] == "cancel":
        current_state = await state.get_state()
        if current_state is None:
            await call.message.answer("Нечего отменять")
        else:
            await state.finish()
            await call.message.answer("Действие отменено")


async def user_input_start(message: types.Message):
    await UserInput.first_name.set()
    await message.answer("Введите ваше ИМЯ: ")


async def user_input_first_name(message: types.Message, state: FSMContext):
    pattern = r"^[-A-ЯЁа-яёA-Za-z]+$"
    if re.match(pattern, message.text) is None:
        await message.answer("Пожалуйста, введите строку, состоящую из букв")
        return
    await state.update_data(first_name=message.text.capitalize())
    await UserInput.next()
    await message.answer("Введите ваше ОТЧЕСТВО (если отсутствует, напишите 'нет'): ")


async def user_input_patronymic_name(message: types.Message, state: FSMContext):
    pattern = r"^[-A-ЯЁа-яёA-Za-z]+$"
    if message.text == 'нет':
        await state.update_data(patronymic_name=None)
    else:
        if re.match(pattern, message.text) is None:
            await message.answer("Пожалуйста, введите строку, состоящую из букв")
            return
        await state.update_data(patronymic_name=message.text.capitalize())
    await UserInput.next()
    await message.answer("Введите вашу ФАМИЛИЮ: ")


async def user_input_last_name(message: types.Message, state: FSMContext):
    pattern = r"^[-A-ЯЁа-яёA-Za-z]+$"
    if re.match(pattern, message.text) is None:
        await message.answer("Пожалуйста, введите строку, состоящую из букв")
        return
    await state.update_data(last_name=message.text.capitalize())
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
    status = user_db_object.add_user(user_data)
    await state.finish()
    if status == STATUS_OK:
        await message.answer("Вы успешно зарегистрированы.")
    elif status == STATUS_USER_ALREADY_EXIST:
        await message.answer("Этот пользователь телеграмма уже есть в нашей базе.")
    else:
        await message.answer("Ой, как же больно! Что-то сломалось внутри меня (")
    # @TODO: вернуть пользователю осмысленное сообщение


async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять")
    else:
        await state.finish()
        await message.answer("Действие отменено")


async def catch_other_message(message: types.Message):
    await message.answer("Неизвестный тип сообщений. Воспользуйся командой /help")


async def additional_info(message: types.Message):
    await message.answer("Тут будет дополнительная информация")


async def get_help_command(message: types.Message):
    await message.answer(
        "* Чтобы зарегистрироваться, введите команду /registration\n"
        "* Чтобы получить дополнительную информацию, введите команду /add_info\n"
        "* Чтобы отменить ввод, введите команду /cancel или напишите 'отмена'\n"
    )


async def catch_receipt(message: types.Message):
    driver = DBDriver()
    receipt = {"tg_id": message["from"]["id"],
               "text": message["text"]}
    status = driver.add_receipt(receipt)
    if status == STATUS_OK:
        await message.answer("Чек принят!")
    elif status == STATUS_RECEIPT_ALREADY_EXIST:
        await message.answer("Этот чек уже есть в нашей базе.")
    elif status == STATUS_RECEIPT_UNKNOWN_USER:
        await message.answer("Что-то я тебя не узнаю. Пожалуйста, зарегистрируйся, а потом отправь чек ещё раз")
    else:
        await message.answer("Ой, как же больно! Что-то сломалось внутри меня.")


async def get_email_for_sending(message: types.Message):
    await SendingMail.email.set()
    await message.answer("Пожалуйста, напишите e-mail для отправки файла: ")


async def get_receipts(message: types.Message, state: FSMContext):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, message.text) is None:
        await message.answer("Пожалуйста, напишите e-mail в формате user@example.com")
        return
    await state.update_data(email=message.text)
    user_data = await state.get_data()
    await state.finish()

    driver = DBDriver()
    status = driver.add_email_for_sending(user_data["email"])
    if status == STATUS_FAIL:
        await message.answer("Ой, как же больно! Что-то сломалось внутри меня.")
    else:
        if status == STATUS_OK:
            await message.answer("E-mail добавлен в базу")
        elif status == STATUS_MAIL_ALREADY_EXIST:
            await message.answer("E-mail уже есть в базе")
        mail = driver.get_email_for_sending(user_data["email"])
        json = driver.get_receipts()
        excel_filepath = json_to_excel(json)
        status = send_email(mail, excel_filepath)
        if status == STATUS_OK:
            await message.answer("Вложение отправлено получателю. Необходимо проверить e-mail")
        else:
            await message.answer("Сбой отправки сообщения")
        os.remove(excel_filepath)
