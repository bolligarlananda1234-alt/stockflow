from app.database import get_connection


def test_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)

        tables = cursor.fetchall()

        return [table[0] for table in tables]

    finally:
        connection.close()