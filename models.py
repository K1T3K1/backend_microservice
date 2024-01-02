from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, DECIMAL, Date
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
import enum
from database import Base


class UserTransaction(Base):
    __tablename__ = 'user_transaction'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transaction.id', ondelete='CASCADE'), primary_key=True)
    
    transaction = relationship("Transaction", back_populates="users")
    user = relationship("User", back_populates="transactions")



class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False)
    
    transactions = relationship("UserTransaction", back_populates="user")






class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), unique=True, nullable=False)
    company_symbol = Column(String(10), unique=True, nullable=False)
    transactions = relationship("Transaction", back_populates="company")


class TransactionType(enum.Enum):
    BUY = 'buy'
    SELL = 'sell'


class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(Enum(TransactionType))
    company_id = Column(Integer, ForeignKey('company.id'))
    
    users = relationship("UserTransaction", back_populates="transaction")
    company = relationship("Company", back_populates="transactions")
