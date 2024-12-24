from app.config import *
from app.userbot.usserbot_functions import *
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
        logger.error(f"Ошибка в process_trigger_step: {e}")


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
                logger.error(f"Ошибка при добавлении триггера: {e}")
            finally:
                conn.close()
                if message.from_user.id in user_data:
                    del user_data[message.from_user.id]
    except Exception as e:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /add_trigger")
        logger.error(f"Ошибка в process_response_step: {e}")


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
    except Exception:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /add_trigger")


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
            except Exception as e:
                control_bot.reply_to(message, f"❌ Ошибка при добавлении триггера: {e}")
            finally:
                conn.close()
                if message.from_user.id in user_data:
                    del user_data[message.from_user.id]
    except Exception as e:
        control_bot.reply_to(message, "Произошла ошибка. Попробуйте снова /add_trigger")


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
                else:
                    control_bot.reply_to(message, f"❌ Триггер '{trigger_word}' не найден")
            conn.close()
    except IndexError:
        control_bot.reply_to(message, "⚠️ Используйте формат: /delete_trigger триггер_для_удаления")
    except Exception as e:
        control_bot.reply_to(message, f"❌ Ошибка при удалении триггера: {e}")





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




def run_control_bot():
    while True:
        try:
            control_bot.polling(none_stop=True, interval=1)
        except Exception as e:
            logger.error(traceback.format_exc())
            time.sleep(3)