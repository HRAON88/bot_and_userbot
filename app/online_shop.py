from telebot.states import StatesGroup

from app.config import *
from app.db import *
from bot.settings_bot import run_control_bot
from userbot.usserbot_functions import run_userbot


class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_time = State()





def main():
    try:
        if not check_database():
            if not fix_database_structure():
                return
            if not check_database():
                return


        control_thread = Thread(target=run_control_bot)
        control_thread.daemon = True
        control_thread.start()
        run_userbot()

    except Exception as e:
        logger.error(f"Ошибка при запуске: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()