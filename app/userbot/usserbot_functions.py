from app.db import *

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
                                logger.error(f"Ошибка в отправке сообщения {user_id}: {e}")

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

        @userbot.on_message(filters.private)
        async def message_handler(client, message):
            await handle_user_message(client, message)

        await userbot.start()

        await asyncio.create_task(check_broadcasts())

        me = await userbot.get_me()

        await idle()

    except Exception as e:
        logger.error(traceback.format_exc())



async def handle_user_message(client, message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        conn = get_db_connection()
        if not conn:
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
        logger.error(f"Ошибка в handle_user_message: {e}")
        raise


def run_userbot():
    try:
        userbot.run(start_userbot())
    except Exception as e:
        logger.error(traceback.format_exc())