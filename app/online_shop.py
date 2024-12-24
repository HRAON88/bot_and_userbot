from telebot.states import StatesGroup

from app.config import *
from app.db import *



class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_time = State()



@control_bot.message_handler(commands=['start'])
def start_control(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        control_bot.reply_to(message, "У вас нет доступа к этому боту.")
        return
    control_bot.reply_to(message, """
Панель управления юзерботом.
Доступные команды:

/add_trigger - Добавить новый триггер
/list_triggers - Список всех триггеров
/delete_trigger - Удалить триггер
/check_db - Проверить состояние базы данных
/schedule_broadcast - Запланировать рассылку
/list_broadcasts - Список запланированных рассылок
/cancel_broadcast - Отменить рассылку
    """)


@control_bot.message_handler(commands=['check_db'])
def handle_check_db(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        control_bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    try:
        control_bot.reply_to(message, "🔍 Начинаю проверку базы данных...")
        if check_database():
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM users")
                    users_count = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM triggers")
                    triggers_count = cur.fetchone()[0]

                    response = (
                        "✅ База данных работает корректно\n\n"
                        f"📊 Статистика:\n"
                        f"👥 Пользователей: {users_count}\n"
                        f"🎯 Триггеров: {triggers_count}"
                    )
                control_bot.reply_to(message, response)
                conn.close()
        else:
            control_bot.reply_to(message, "❌ Обнаружены проблемы с базой данных")

    except Exception as e:
        error_message = f"❌ Ошибка при проверке базы данных: {str(e)}"
        logger.error(error_message)
        control_bot.reply_to(message, error_message)


@control_bot.message_handler(commands=['add_trigger'])
def start_add_trigger(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    msg = control_bot.reply_to(message, "Отправьте триггерное слово или фразу:")
    control_bot.register_next_step_handler(msg, process_trigger_step)


def process_trigger_step(message):
    try:
        if str(message.from_user.id) != str(ADMIN_ID):
            return

        trigger = message.text
        user_data[message.from_user.id] = {'trigger': trigger}

        msg = control_bot.reply_to(message, "Теперь отправьте текст ответа:")
        control_bot.register_next_step_handler(msg, process_response_step)
    except Exception as e:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /add_trigger")
        logger.error(f"Error in process_trigger_step: {e}")


def process_response_step(message):
    try:
        if str(message.from_user.id) != str(ADMIN_ID):
            return


        trigger = user_data[message.from_user.id]['trigger']
        response = message.text

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO triggers (trigger_word, response_text) VALUES (%s, %s)",
                        (trigger, response)
                    )
                    conn.commit()
                control_bot.reply_to(message, f"✅ Триггер '{trigger}' успешно добавлен!")
                logger.info(f"New trigger added: {trigger}")
            except Exception as e:
                control_bot.reply_to(message, f"❌ Ошибка при добавлении триггера: {e}")
                logger.error(f"Error adding trigger: {e}")
            finally:
                conn.close()
                if message.from_user.id in user_data:
                    del user_data[message.from_user.id]
    except Exception as e:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /add_trigger")
        logger.error(f"Error in process_response_step: {e}")


@control_bot.message_handler(commands=['list_triggers'])
def list_triggers(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT trigger_word, response_text FROM triggers")
                triggers = cur.fetchall()

                if triggers:
                    response = "📝 Список активных триггеров:\n\n"
                    for i, (trigger, response_text) in enumerate(triggers, 1):
                        response += f"{i}. Триггер: {trigger}\nОтвет: {response_text}\n{'=' * 30}\n"

                    if len(response) > 4000:
                        parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
                        for part in parts:
                            control_bot.reply_to(message, part)
                    else:
                        control_bot.reply_to(message, response)
                else:
                    control_bot.reply_to(message, "❌ Триггеры отсутствуют")
        except Exception as e:
            control_bot.reply_to(message, f"❌ Ошибка при получении списка триггеров: {e}")
            logger.error(f"Error listing triggers: {e}")
        finally:
            conn.close()


@control_bot.message_handler(commands=['start'])
def start_control(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        control_bot.reply_to(message, "У вас нет доступа к этому боту.")
        return
    control_bot.reply_to(message, """
Панель управления юзерботом.
Доступные команды:

/add_trigger - Добавить новый триггер
/list_triggers - Список всех триггеров
/delete_trigger - Удалить триггер
/check_db - Проверить состояние базы данных
    """)


@control_bot.message_handler(commands=['check_db'])
def handle_check_db(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        control_bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    try:
        control_bot.reply_to(message, "🔍 Начинаю проверку базы данных...")
        if check_database():
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM users")
                    users_count = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM triggers")
                    triggers_count = cur.fetchone()[0]

                    response = (
                        "✅ База данных работает корректно\n\n"
                        f"📊 Статистика:\n"
                        f"👥 Пользователей: {users_count}\n"
                        f"🎯 Триггеров: {triggers_count}"
                    )
                control_bot.reply_to(message, response)
                conn.close()
        else:
            control_bot.reply_to(message, "❌ Обнаружены проблемы с базой данных")

    except Exception as e:
        error_message = f"❌ Ошибка при проверке базы данных: {str(e)}"
        logger.error(error_message)
        control_bot.reply_to(message, error_message)


@control_bot.message_handler(commands=['add_trigger'])
def start_add_trigger(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    msg = control_bot.reply_to(message, "Отправьте триггерное слово или фразу:")
    control_bot.register_next_step_handler(msg, process_trigger_step)


def process_trigger_step(message):
    try:
        if str(message.from_user.id) != str(ADMIN_ID):
            return

        trigger = message.text
        user_data[message.from_user.id] = {'trigger': trigger}

        msg = control_bot.reply_to(message, "Теперь отправьте текст ответа:")
        control_bot.register_next_step_handler(msg, process_response_step)
    except Exception as e:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /add_trigger")
        logger.error(f"Error in process_trigger_step: {e}")


def process_response_step(message):
    try:
        if str(message.from_user.id) != str(ADMIN_ID):
            return

        trigger = user_data[message.from_user.id]['trigger']
        response = message.text

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO triggers (trigger_word, response_text) VALUES (%s, %s)",
                        (trigger, response)
                    )
                    conn.commit()
                control_bot.reply_to(message, f"✅ Триггер '{trigger}' успешно добавлен!")
                logger.info(f"New trigger added: {trigger}")
            except Exception as e:
                control_bot.reply_to(message, f"❌ Ошибка при добавлении триггера: {e}")
                logger.error(f"Error adding trigger: {e}")
            finally:
                conn.close()
                if message.from_user.id in user_data:
                    del user_data[message.from_user.id]
    except Exception as e:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /add_trigger")
        logger.error(f"Error in process_response_step: {e}")


@control_bot.message_handler(commands=['list_triggers'])
def list_triggers(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT trigger_word, response_text FROM triggers")
                triggers = cur.fetchall()

                if triggers:
                    response = "📝 Список активных триггеров:\n\n"
                    for i, (trigger, response_text) in enumerate(triggers, 1):
                        response += f"{i}. Триггер: {trigger}\nОтвет: {response_text}\n{'=' * 30}\n"

                    if len(response) > 4000:
                        parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
                        for part in parts:
                            control_bot.reply_to(message, part)
                    else:
                        control_bot.reply_to(message, response)
                else:
                    control_bot.reply_to(message, "❌ Триггеры отсутствуют")
        except Exception as e:
            control_bot.reply_to(message, f"❌ Ошибка при получении списка триггеров: {e}")
            logger.error(f"Error listing triggers: {e}")
        finally:
            conn.close()


@control_bot.message_handler(commands=['delete_trigger'])
def delete_trigger(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return

    try:
        trigger_word = message.text.split(maxsplit=1)[1]
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM triggers WHERE trigger_word = %s RETURNING trigger_word",
                    (trigger_word,)
                )
                deleted = cur.fetchone()
                conn.commit()

                if deleted:
                    control_bot.reply_to(message, f"✅ Триггер '{trigger_word}' успешно удален")
                    logger.info(f"Trigger deleted: {trigger_word}")
                else:
                    control_bot.reply_to(message, f"❌ Триггер '{trigger_word}' не найден")
            conn.close()
    except IndexError:
        control_bot.reply_to(message, "⚠️ Используйте формат: /delete_trigger триггер_для_удаления")
    except Exception as e:
        control_bot.reply_to(message, f"❌ Ошибка при удалении триггера: {e}")
        logger.error(f"Error deleting trigger: {e}")


async def handle_user_message(client, message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        conn = get_db_connection()
        if not conn:
            logger.error("Failed to get database connection")
            return

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
                user_exists = cur.fetchone()

                if not user_exists:
                    cur.execute(
                        "INSERT INTO users (user_id, username) VALUES (%s, %s)",
                        (user_id, username)
                    )
                    conn.commit()
                    logger.info(f"New user registered: {username}")

                cur.execute("SELECT trigger_word, response_text FROM triggers")
                triggers = cur.fetchall()

                message_text = message.text.lower() if message.text else ""
                trigger_found = False

                for trigger_word, response_text in triggers:
                    if trigger_word.lower() in message_text:
                        await client.send_message(user_id, response_text)
                        trigger_found = True
                        break

                if not trigger_found and ADMIN_ID:
                    await client.send_message(user_id, "Подождите, я позову администратора.")
                    await client.send_message(ADMIN_ID,
                                           f"❗️ Новое сообщение:\n"
                                           f"От: @{username}\n"
                                           f"Текст: {message_text}")

        finally:
            conn.close()

    except Exception as e:
        logger.error(f"Error in handle_user_message: {e}")
        raise


@control_bot.message_handler(commands=['schedule_broadcast'])
def start_schedule_broadcast(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    msg = control_bot.reply_to(message, "Отправьте текст сообщения для рассылки:")
    control_bot.register_next_step_handler(msg, process_broadcast_message)


def process_broadcast_message(message):
    try:
        if str(message.from_user.id) != str(ADMIN_ID):
            return

        user_data[message.from_user.id] = {'broadcast_message': message.text}

        msg = control_bot.reply_to(message,
                                   "Отправьте время рассылки в формате YYYY-MM-DD HH:MM\n"
                                   "Например: 2024-12-31 23:59")
        control_bot.register_next_step_handler(msg, process_broadcast_time)
    except Exception as e:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /schedule_broadcast")
        logger.error(f"Error in process_broadcast_message: {e}")


def process_broadcast_time(message):
    try:
        if str(message.from_user.id) != str(ADMIN_ID):
            return

        scheduled_time = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
        broadcast_message = user_data[message.from_user.id]['broadcast_message']

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO broadcasts (message_text, scheduled_time) VALUES (%s, %s)",
                        (broadcast_message, scheduled_time)
                    )
                    conn.commit()
                control_bot.reply_to(message,
                                     f"✅ Рассылка запланирована на {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            except Exception as e:
                control_bot.reply_to(message, f"❌ Ошибка при планировании рассылки: {e}")
            finally:
                conn.close()
                if message.from_user.id in user_data:
                    del user_data[message.from_user.id]
    except ValueError:
        control_bot.reply_to(message, "❌ Неверный формат времени. Используйте формат YYYY-MM-DD HH:MM")
    except Exception as e:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /schedule_broadcast")


@control_bot.message_handler(commands=['list_broadcasts'])
def list_broadcasts(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, message_text, scheduled_time, status 
                    FROM broadcasts 
                    WHERE status = 'pending'
                    ORDER BY scheduled_time
                """)
                broadcasts = cur.fetchall()

                if broadcasts:
                    response = "📝 Запланированные рассылки:\n\n"
                    for id, text, time, status in broadcasts:
                        response += f"ID: {id}\nТекст: {text}\nВремя: {time}\nСтатус: {status}\n{'=' * 30}\n"
                    control_bot.reply_to(message, response)
                else:
                    control_bot.reply_to(message, "Нет запланированных рассылок")
        finally:
            conn.close()


@control_bot.message_handler(commands=['cancel_broadcast'])
def cancel_broadcast(message):
    try:
        broadcast_id = int(message.text.split()[1])
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE broadcasts SET status = 'cancelled' WHERE id = %s AND status = 'pending'",
                        (broadcast_id,)
                    )
                    conn.commit()
                    if cur.rowcount > 0:
                        control_bot.reply_to(message, f"✅ Рассылка {broadcast_id} отменена")
                    else:
                        control_bot.reply_to(message, f"❌ Рассылка {broadcast_id} не найдена")
            finally:
                conn.close()
    except (IndexError, ValueError):
        control_bot.reply_to(message, "Используйте формат: /cancel_broadcast ID")


async def check_broadcasts():
    try:
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, message_text 
                        FROM broadcasts 
                        WHERE status = 'pending' 
                        AND scheduled_time <= NOW()
                    """)
                    broadcasts = cur.fetchall()

                    for broadcast_id, message_text in broadcasts:
                        cur.execute("SELECT user_id FROM users")
                        users = cur.fetchall()

                        for (user_id,) in users:
                            try:

                                if hasattr(userbot, 'send_message'):
                                    await userbot.send_message(user_id, message_text)
                                await asyncio.sleep(0.1)
                            except Exception as e:
                                logger.error(f"Error sending broadcast to user {user_id}: {e}")

                        cur.execute(
                            "UPDATE broadcasts SET status = 'completed' WHERE id = %s",
                            (broadcast_id,)
                        )
                        conn.commit()
            finally:
                conn.close()
    except Exception as e:
        logger.error(f"Error in check_broadcasts: {e}")
        raise
async def start_userbot():
    try:
        logger.info("Starting userbot...")

        @userbot.on_message(filters.private)
        async def message_handler(client, message):
            await handle_user_message(client, message)

        await userbot.start()
        logger.info("Userbot started successfully")

        asyncio.create_task(check_broadcasts())

        me = await userbot.get_me()
        logger.info(f"Userbot is running as: {me.first_name} ({me.id})")

        await idle()

    except Exception as e:
        logger.error(f"Error in start_userbot: {str(e)}")
        logger.error(traceback.format_exc())

def run_userbot():
    """Запуск юзербота в отдельном потоке"""
    try:
        logger.info("Initializing userbot thread")
        userbot.run(start_userbot())
    except Exception as e:
        logger.error(f"Error in run_userbot: {str(e)}")
        logger.error(traceback.format_exc())

def run_control_bot():
    logger.info("Starting control bot...")
    while True:
        try:
            control_bot.polling(none_stop=True, interval=1)
        except Exception as e:
            logger.error(f"Control bot error: {str(e)}")
            logger.error(traceback.format_exc())
            time.sleep(3)

def main():
    try:
        logger.info("Starting application...")


        logger.info("Performing initial database check...")
        if not check_database():
            logger.info("Initial database check failed, attempting to fix...")
            if not fix_database_structure():
                logger.error("Failed to fix database structure")
                return
            if not check_database():
                logger.error("Database check failed after fixing")
                return


        control_thread = Thread(target=run_control_bot)
        control_thread.daemon = True
        control_thread.start()
        logger.info("Control bot thread started")


        logger.info("Starting userbot in main thread...")
        run_userbot()

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    print("процесс запущен")
    main()