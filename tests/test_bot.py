import pytest
from app.db import get_db_connection
from conftest import TEST_DB_NAME, TEST_DB_USER, TEST_DB_PASSWORD, TEST_DB_HOST

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

        from app.online_shop import handle_user_message
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