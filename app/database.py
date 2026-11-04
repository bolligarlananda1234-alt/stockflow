import pyodbc

SERVER = r"Bolligarla\SQLEXPRESS"
DATABASE = "StockFlowDB"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def get_connection():
    return pyodbc.connect(CONNECTION_STRING)


def get_db():
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()