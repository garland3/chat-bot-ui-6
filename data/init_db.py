
import sqlite3

def init_db():
    conn = sqlite3.connect('./data/app.db')
    cursor = conn.cursor()

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')

    # Create payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    # Insert sample data into customers
    customers_data = [
        ('Alice Smith', 'alice@example.com'),
        ('Bob Johnson', 'bob@example.com'),
        ('Charlie Brown', 'charlie@example.com'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO customers (name, email) VALUES (?, ?)
    ''', customers_data)

    # Insert sample data into payments
    payments_data = [
        (1, 100.00),
        (1, 50.00),
        (2, 75.50),
        (3, 120.00),
    ]
    cursor.executemany('''
        INSERT INTO payments (customer_id, amount) VALUES (?, ?)
    ''', payments_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
