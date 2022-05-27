import logging

from aiogram.types import BotCommand


def setup_logging(logfile='log.txt', loglevel='DEBUG'):
    """

    :param logfile:
    :param loglevel:
    :return:
    """
    loglevel = getattr(logging, loglevel)

    logger = logging.getLogger()
    logger.setLevel(loglevel)
    fmt = '%(asctime)s: %(levelname)s: %(filename)s: ' + \
          '%(funcName)s(): %(lineno)d: %(message)s'
    formatter = logging.Formatter(fmt)

    fh = logging.FileHandler(logfile, encoding='utf-8')
    fh.setLevel(loglevel)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "Запуск"),
        BotCommand("help", "Помощь"),
        BotCommand("registration", "Зарегистрироваться"),
        BotCommand("add_info", "Доп. информация"),
        BotCommand("cancel", "Отменить текущее действие")
    ])
