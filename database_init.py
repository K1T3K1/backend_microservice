import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB')
)

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        company_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        company_id INT NOT NULL,
        amount INT NOT NULL,
        price_per_unit DECIMAL(10, 2) NOT NULL,
        transaction_date DATE NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(company_id) REFERENCES companies(company_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolios (
        portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        company_id INT NOT NULL,
        amount INT NOT NULL,
        avg_price DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(company_id) REFERENCES companies(company_id)
    )
''')

conn.commit()
cursor.close()

