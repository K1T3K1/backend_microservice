from sqlalchemy.orm import Session
from faker import Faker
from database import SessionLocal
from models import User, Company, Transaction, TransactionType

fake = Faker()

db = SessionLocal()


users = []
for _ in range(50):
    user = User(
        username=fake.user_name(),
        password_hash=fake.password(),
        email=fake.email(),
        last_login_date=fake.date_time_between(start_date="-30d", end_date="now"),
    )
    users.append(user)

db.add_all(users)
db.commit()


companies = []
for _ in range(50):
    company = Company(
        company_name=fake.company(),
        company_symbol=fake.pystr(min_chars=2, max_chars=4),  
    )
    companies.append(company)

db.add_all(companies)
db.commit()

transactions = []
for _ in range(50):
    transaction = Transaction(
        amount=fake.random_int(min=1, max=100),
        price_per_unit=fake.pydecimal(left_digits=4, right_digits=2, positive=True),
        transaction_date=fake.date_between(start_date="-30d", end_date="now"),
        transaction_type=fake.random_element(TransactionType),
        users=fake.random_elements(elements=users, length=fake.random_int(min=1, max=5), unique=True),
        company=fake.random_element(companies),
    )
    transactions.append(transaction)

db.add_all(transactions)
db.commit()

db.close()
