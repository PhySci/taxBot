from aiogram import types
from aiogram.dispatcher.filters import Command, BoundFilter

from src.settings import SUPERUSER_IDS


class IsAdmin(BoundFilter):
    key = "is_admin"

    def __init__(self, commands: Command):
        self.commands = commands

    async def check(self, message: types.Message) -> bool:
        admins = SUPERUSER_IDS.split(',')
        user = message.from_user.id
        if str(user) not in admins:
            await message.answer('Вы не являетесь администратором')
            return False
        return message.text[1:] in self.commands.commands
