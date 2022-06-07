import os
import logging
from dotenv import load_dotenv

load_dotenv()

_logger = logging.getLogger(__name__)


BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'

WEBAPP_PORT = os.getenv('WEBAPP_PORT')

ROOT_URL = os.getenv('ROOT_URL')


# is local development?
LOCAL_DEV = os.getenv('LOCAL_DEV')

# Variables for e-mail sending
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
