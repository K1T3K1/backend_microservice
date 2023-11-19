from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Date
from database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index = True)
    username = Column(String(255), unique=True, nullable=False)

class Company(Base):
    __tablename__ = 'companies'
    company_id = Column(Integer, primary_key=True, index = True)
    company_name = Column(String(255), unique=True, nullable=False)
    company_symbol = Column(String(10), unique=True, nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer, primary_key=True, index = True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    company_id = Column(Integer, ForeignKey('companies.company_id'))
    amount = Column(Integer, nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)