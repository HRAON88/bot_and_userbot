import pyrogram
import telebot
import logging
import psycopg2
from datetime import datetime
import time
from pyrogram import Client, filters
import asyncio
from threading import Thread
import nest_asyncio
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import sys
import traceback
from pyrogram import Client, filters, idle
from dotenv import load_dotenv
import os
import os
import logging
import nest_asyncio
from dotenv import load_dotenv
from telebot.storage import StateMemoryStorage
from telebot import TeleBot
from pyrogram import Client


load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN', 'try')
ADMIN_ID = int(os.getenv('ADMIN_ID', 'try'))
API_ID = int(os.getenv('API_ID', 'try'))
API_HASH = os.getenv('API_HASH', 'try')
SESSION_STRING = os.getenv('SESSION_STRING',
'try')

DB_NAME = os.getenv('DB_NAME', 'userbot_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'try')
DB_HOST = os.getenv('DB_HOST', 'localhost')


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)


for logger_name in ['pyrogram', 'telebot', 'urllib3', 'asyncio', 'schedule']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


user_data = {}


nest_asyncio.apply()



def create_control_bot():
    return TeleBot(
        BOT_TOKEN,
        parse_mode='HTML',
        state_storage=StateMemoryStorage()
    )


def create_userbot():
    return Client(
        "my_userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )

control_bot = create_control_bot()
userbot = create_userbot()


def check_config():
    required_vars = {
        'BOT_TOKEN': BOT_TOKEN,
        'ADMIN_ID': ADMIN_ID,
        'API_ID': API_ID,
        'API_HASH': API_HASH,
        'SESSION_STRING': SESSION_STRING,
        'DB_NAME': DB_NAME,
        'DB_USER': DB_USER,
        'DB_PASSWORD': DB_PASSWORD,
        'DB_HOST': DB_HOST
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        logger.error(f"Missing required configuration variables: {', '.join(missing_vars)}")
        return False

    logger.info("Configuration check passed successfully")
    return True

if not check_config():
    logger.error("Invalid configuration. Please check your environment variables.")
    raise ValueError("Invalid configuration")
