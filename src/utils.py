import logging
from logging.handlers import TimedRotatingFileHandler
import os


def setup_logging(logfile=None, loglevel='DEBUG'):
    """

    :param logfile:
    :param loglevel:
    :return:
    """
    if logfile is None:
        logfile = os.path.join(os.path.dirname(__file__), "logs/taxbot")

    loglevel = getattr(logging, loglevel)

    logger = logging.getLogger()
    logger.setLevel(loglevel)
    fmt = '%(asctime)s: %(levelname)s: %(filename)s: ' + \
          '%(funcName)s(): %(lineno)d: %(message)s'
    formatter = logging.Formatter(fmt)

    fh = TimedRotatingFileHandler(filename=logfile, when="D", interval=1, encoding="utf-8")
    fh.setLevel(loglevel)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)


