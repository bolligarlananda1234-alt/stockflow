
from app.database import get_connection

def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Organizations (
        organization_id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_name TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organization_id)
            REFERENCES Organizations(organization_id)
    );

    CREATE TABLE IF NOT EXISTS Settings (
        setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL UNIQUE,
        default_low_stock_threshold INTEGER NOT NULL DEFAULT 5,
        CHECK (default_low_stock_threshold >= 0),
        FOREIGN KEY (organization_id)
            REFERENCES Organizations(organization_id)
    );

    CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        sku TEXT NOT NULL,
        description TEXT,
        quantity INTEGER NOT NULL DEFAULT 0,
        cost_price REAL NOT NULL DEFAULT 0,
        selling_price REAL NOT NULL DEFAULT 0,
        low_stock_threshold INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (organization_id, sku),
        CHECK (quantity >= 0),
        CHECK (cost_price >= 0),
        CHECK (selling_price >= 0),
        CHECK (low_stock_threshold IS NULL OR low_stock_threshold >= 0),
        FOREIGN KEY (organization_id)
            REFERENCES Organizations(organization_id)
    );
    """)

    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    create_tables()
    print("SQLite tables created successfully!")
