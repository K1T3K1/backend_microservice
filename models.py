from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Date
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
import enum
from database import Base

class UsersTransactions(Base):
    __tablename__ = 'user_transaction'
    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transaction.transaction_id'), primary_key=True)



class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False)


class Company(Base):
    __tablename__ = 'company'
    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), unique=True, nullable=False)
    company_symbol = Column(String(10), unique=True, nullable=False)

class TransactionType(enum.Enum):
    BUY = 'buy'
    SELL = 'sell'

class Transaction(Base):
    __tablename__ = 'transaction'
    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    company_id = Column(Integer, ForeignKey('company.company_id'))
    amount = Column(Integer, nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(Enum(TransactionType))
    users = relationship("User", secondary=UsersTransactions, back_populates="transaction")

