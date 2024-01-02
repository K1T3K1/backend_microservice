from datetime import date, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from authorization import validate_jwt
from models import UserTransaction, Transaction
from utils import get_db
from database import get_influx_client

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]

router = APIRouter(
    tags=['user']
)


class TransactionRequest(BaseModel):
    id: int


class TransactionResult(BaseModel):
    status: str


class TransactionModel(BaseModel):
    id: Optional[int] = 0
    amount: int
    price_per_unit: float
    transaction_date: date
    transaction_type: str
    company_id: int


class TransactionListModel(BaseModel):
    transactions: list[TransactionModel]


class CompanyCandleStickModel(BaseModel):
    time: datetime
    OpenPrice: float
    HighPrice: float
    LowPrice: float
    ClosePrice: float
    Volume: int

class CompanyCandleStickListModel(BaseModel):
    candlesticks: list[CompanyCandleStickModel]


@router.put('/user/transaction', status_code=status.HTTP_200_OK, response_model=TransactionResult)
async def create_transaction(user: user_dependency, db: db_dependency, transaction_obj: TransactionModel):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user_id = user['id']

    if transaction_obj.id != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction id must be 0")

    transaction = Transaction(
        amount=transaction_obj.amount,
        price_per_unit=transaction_obj.price_per_unit,
        transaction_date=transaction_obj.transaction_date,
        transaction_type=transaction_obj.transaction_type,
        company_id=transaction_obj.company_id
    )

    db.add(transaction)
    db.commit()

    user_transaction = UserTransaction(
        user_id=user_id,
        transaction_id=transaction.id
    )

    db.add(user_transaction)
    db.commit()

    return {'status': 'success'}


@router.delete('/user/transaction', status_code=status.HTTP_200_OK, response_model=TransactionResult)
async def delete_transaction(user: user_dependency, db: db_dependency, token: TransactionRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    # get transaction id from request
    transaction_id = token.id
    user_id = user['id']

    # get user_transaction from db where transaction id and user id match
    user_transaction = (
        db.query(UserTransaction)
        .filter(UserTransaction.transaction_id == transaction_id)
        .filter(UserTransaction.user_id == user_id)
        .first()
    )

    # if user_transaction is not found, raise 404
    if user_transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    # delete user_transaction
    db.delete(user_transaction)
    db.commit()

    # get transaction from db
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    # if transaction is not found, raise 404
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    # delete transaction
    db.delete(transaction)
    db.commit()

    return {'status': 'success'}



@router.post('/user/transaction', status_code=status.HTTP_200_OK, response_model=TransactionResult)
async def update_transaction(user: user_dependency, db: db_dependency, transaction_obj: TransactionModel):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user_id = user['id']

    transaction = (
        db.query(Transaction)
        .join(UserTransaction)
        .filter(UserTransaction.transaction_id == transaction_obj.id)
        .filter(UserTransaction.user_id == user_id)
        .first()
    )

    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    transaction.amount = transaction_obj.amount
    transaction.price_per_unit = transaction_obj.price_per_unit
    transaction.transaction_date = transaction_obj.transaction_date
    transaction.transaction_type = transaction_obj.transaction_type
    transaction.company_id = transaction_obj.company_id

    db.commit()

    return {'status': 'success'}


@router.get('/user/transactions', status_code=status.HTTP_200_OK, response_model=TransactionListModel)
async def get_all_transactions(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user_id = user['id']

    transactions = (
        db.query(Transaction)
        .join(UserTransaction)
        .filter(UserTransaction.user_id == user_id)
        .all()
    )

    return {'transactions': transactions}


@router.get('/company/chart/candlestick', status_code=status.HTTP_200_OK, response_model=CompanyCandleStickListModel)
async def get_company_candle_chart(company: str = "XD", range: str = "7d"):
    client = await get_influx_client()
    data = await client.query_data(range, company)
    if data is None or data.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for company")

    records = []
    for index, row in data.iterrows():
        record = CompanyCandleStickModel(
            time=row['_time'].to_pydatetime(),
            OpenPrice=row['OpenPrice'],
            HighPrice=row['HighPrice'],
            LowPrice=row['LowPrice'],
            ClosePrice=row['ClosePrice'],
            Volume=row['Volume']
        )
        records.append(record)

    return CompanyCandleStickListModel(candlesticks=records)
