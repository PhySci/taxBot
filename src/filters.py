from aiogram import types
from aiogram.dispatcher.filters import Filter, Command


class CommandNotInListFilter(Filter):
    def __init__(self, commands: Command):
        self.commands = commands

    async def check(self, message: types.Message) -> bool:
        if message.text.startswith('/'):
            return message.text[1:] in self.commands.commands
