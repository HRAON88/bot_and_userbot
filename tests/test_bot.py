import asyncio
from datetime import datetime, timedelta

import pytest
from app.db import get_db_connection
from app.config import userbot
from conftest import TEST_DB_NAME, TEST_DB_USER, TEST_DB_PASSWORD, TEST_DB_HOST
from app.userbot.usserbot_functions import handle_user_message, check_broadcasts, start_userbot


@pytest.mark.asyncio
async def test_handle_message(db_cursor, mock_message, mock_userbot, monkeypatch):
    monkeypatch.setenv('DB_NAME', TEST_DB_NAME)
    monkeypatch.setenv('DB_USER', TEST_DB_USER)
    monkeypatch.setenv('DB_PASSWORD', TEST_DB_PASSWORD)
    monkeypatch.setenv('DB_HOST', TEST_DB_HOST)

    from app import config
    monkeypatch.setattr(config, 'DB_NAME', TEST_DB_NAME)
    monkeypatch.setattr(config, 'DB_USER', TEST_DB_USER)
    monkeypatch.setattr(config, 'DB_PASSWORD', TEST_DB_PASSWORD)
    monkeypatch.setattr(config, 'DB_HOST', TEST_DB_HOST)

    try:
        test_conn = get_db_connection()
        if not test_conn:
            raise Exception("Could not connect to test database!")
        test_conn.close()

        test_user_id = 12345
        test_username = "test_user"
        test_message_text = "test message"

        mock_message.from_user.id = test_user_id
        mock_message.from_user.username = test_username
        mock_message.text = test_message_text

        db_cursor.execute("DELETE FROM users")
        db_cursor.connection.commit()

        db_cursor.execute("SELECT COUNT(*) FROM users")
        users_before = db_cursor.fetchone()[0]

        await handle_user_message(mock_userbot, mock_message)

        verify_conn = get_db_connection()
        try:
            with verify_conn.cursor() as verify_cur:
                verify_cur.execute("SELECT * FROM users")
                verify_cur.execute(
                    "SELECT user_id, username FROM users WHERE user_id = %s",
                    (test_user_id,)
                )
                user_result = verify_cur.fetchone()

                assert user_result is not None, "User was not added to database!"
                assert user_result[0] == test_user_id, f"Expected user_id {test_user_id}, got {user_result[0]}"
        finally:
            verify_conn.close()

        mock_userbot.send_message.assert_called()

    except Exception as e:
        raise

    finally:
        cleanup_conn = get_db_connection()
        try:
            with cleanup_conn.cursor() as cleanup_cur:
                cleanup_cur.execute("DELETE FROM users")
                cleanup_conn.commit()
        finally:
            cleanup_conn.close()

@pytest.mark.asyncio
async def test_userbot_message_handling(db_cursor, mock_userbot):
    try:
        test_user_id = 12345
        test_username = "test_user"
        test_message_text = "привет"
        test_trigger = "привет"
        test_response = "здравствуйте"

        sent_messages = []

        async def mock_send_message(user_id, text):
            sent_messages.append({'user_id': user_id, 'text': text})
            return True

        mock_userbot.send_message = mock_send_message

        mock_message = type('MockMessage', (), {
            'from_user': type('MockUser', (), {
                'id': test_user_id,
                'username': test_username
            }),
            'text': test_message_text
        })

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users")
            cur.execute("DELETE FROM triggers")

            cur.execute(
                "INSERT INTO triggers (trigger_word, response_text) VALUES (%s, %s)",
                (test_trigger, test_response)
            )
            conn.commit()

        await handle_user_message(mock_userbot, mock_message)

        verify_conn = get_db_connection()
        try:
            with verify_conn.cursor() as verify_cur:
                verify_cur.execute("SELECT user_id, username FROM users WHERE user_id = %s", (test_user_id,))
                user_result = verify_cur.fetchone()

                assert user_result is not None, "Пользователь не добавлен в базу"
                assert user_result[0] == test_user_id, "Неверный user_id"
                assert user_result[1] == test_username, "Неверный username"

                assert len(sent_messages) > 0, "Сообщения не были отправлены"
                assert any(msg['text'] == test_response for msg in sent_messages), "Ответ на триггер не отправлен"

        finally:
            verify_conn.close()

    finally:
        cleanup_conn = get_db_connection()
        with cleanup_conn.cursor() as cleanup_cur:
            cleanup_cur.execute("DELETE FROM users")
            cleanup_cur.execute("DELETE FROM triggers")
            cleanup_conn.commit()
        cleanup_conn.close()