import psycopg2

from app.config import *
def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=5432
        )
        connection.autocommit = True
        return connection
    except Exception as e:
        logger.error(f"Ошибка в подключение к базе данных: {str(e)}")
        return None

def check_database():
    try:
        conn = get_db_connection()
        if not conn:
            return False

        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            existing_tables = [table[0] for table in cur.fetchall()]
            required_tables = ['users', 'triggers', 'scheduled_messages', 'broadcasts']
            missing_tables = [table for table in required_tables if table not in existing_tables]

            if missing_tables:
                return False

            return True

    except Exception as e:
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()



def fix_database_structure():
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute('DROP TABLE IF EXISTS users CASCADE')
                cur.execute('DROP TABLE IF EXISTS triggers CASCADE')
                cur.execute('DROP TABLE IF EXISTS scheduled_messages CASCADE')
                cur.execute('DROP TABLE IF EXISTS broadcasts CASCADE')

                cur.execute('''
                    CREATE TABLE users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cur.execute('''
                    CREATE TABLE triggers (
                        id SERIAL PRIMARY KEY,
                        trigger_word TEXT NOT NULL,
                        response_text TEXT NOT NULL
                    )
                ''')

                cur.execute('''
                    CREATE TABLE scheduled_messages (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        message_text TEXT,
                        scheduled_time TIMESTAMP
                    )
                ''')


                cur.execute('''
                    CREATE TABLE broadcasts (
                        id SERIAL PRIMARY KEY,
                        message_text TEXT NOT NULL,
                        scheduled_time TIMESTAMP NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("Успешно изменена структура бд")
            conn.close()
            return True
    except Exception as e:
        return False


def init_database():
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cur.execute('''
                    CREATE TABLE IF NOT EXISTS triggers (
                        id SERIAL PRIMARY KEY,
                        trigger_word TEXT NOT NULL,
                        response_text TEXT NOT NULL
                    )
                ''')

                cur.execute('''
                    CREATE TABLE IF NOT EXISTS scheduled_messages (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        message_text TEXT,
                        scheduled_time TIMESTAMP
                    )
                ''')

                conn.commit()
            conn.close()
            return True
    except Exception as e:
        logger.error(f"Ошибка в инициализации бд: {str(e)}")
        return False
