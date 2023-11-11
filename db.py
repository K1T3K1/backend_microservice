import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Tabela dla użytkowników
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL
    )
''')

# Tabela dla firm na giełdzie
c.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

# Tabela dla transakcji na giełdzie
c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        transaction_date TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(company_id) REFERENCES companies(company_id)
    )
''')

# Tabela dla portfeli użytkowników
c.execute('''
    CREATE TABLE IF NOT EXISTS portfolios (
        portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        avg_price REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(company_id) REFERENCES companies(company_id)
    )
''')