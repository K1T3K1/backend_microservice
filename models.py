from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, DECIMAL, Date
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
import enum
from database import Base

UsersTransactions = Table('users_transactions', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('transaction_id', Integer, ForeignKey('transaction.id'), )
)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False)
    transactions = relationship("Transaction", secondary=UsersTransactions, back_populates="users")


class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), unique=True, nullable=False)
    company_symbol = Column(String(10), unique=True, nullable=False)


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
    users = relationship("User", secondary=UsersTransactions, back_populates="transactions")
