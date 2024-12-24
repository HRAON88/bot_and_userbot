import pytest
from app.db import get_db_connection

TEST_DB_NAME = "test_db"
TEST_DB_USER = "test_user"
TEST_DB_PASSWORD = "test_password"
TEST_DB_HOST = "localhost"

pytest_plugins = ['pytest_asyncio']


@pytest.fixture
def db_cursor():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
    finally:
        conn.close()


@pytest.fixture
def mock_message(mocker):
    message = mocker.Mock()
    message.from_user = mocker.Mock()
    return message


@pytest.fixture
def mock_userbot(mocker):
    mock = mocker.Mock()

    async def async_send_message(*args, **kwargs):
        return None

    mock.send_message = mocker.AsyncMock(side_effect=async_send_message)
    return mock


@pytest.fixture(autouse=True)
def mocker(pytestconfig):
    from pytest_mock import MockerFixture
    return MockerFixture(pytestconfig)