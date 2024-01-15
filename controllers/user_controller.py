from datetime import date, datetime
from typing import Annotated, Optional, List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from authorization import validate_jwt
from models import TransactionType, UserTransaction, Transaction, Company
from utils.utils import get_db
from database import get_influx_client
from utils.metrics import get_metric

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


class CompanyModel(BaseModel):
    id: int
    name: str
    symbol: str
    price_per_unit: float = 0


class CompanyListModel(BaseModel):
    companies: list[CompanyModel]


class SimulatorCompanyModel(BaseModel):
    company_symbol: str
    investment_volume: float  # in dollars


class SimulatorCompanyListModel(BaseModel):
    companies: list[SimulatorCompanyModel]


class SimulatorResultModel(BaseModel):
    roi: float  # return on investment
    stddev: float  # standard deviation
    interval: tuple[float, float]  # interval
    sharpe: float  # sharpe ratio
    recommendation: str


class WalletModel(BaseModel):
    name: str
    amount: int
    average_buy_price: float
    average_sell_price: float


class CompanyByIdModel(BaseModel):
    id: int


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

    transaction_id = token.id
    user_id = user['id']

    user_transaction = (
        db.query(UserTransaction)
        .filter(UserTransaction.transaction_id == transaction_id)
        .filter(UserTransaction.user_id == user_id)
        .filter(UserTransaction.transaction_id == transaction_id)
        .first()
    )

    if user_transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    db.delete(user_transaction)
    db.commit()

    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if transaction is None or user_transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    db.delete(user_transaction)
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


@router.get('/companies', status_code=status.HTTP_200_OK, response_model=CompanyListModel)
async def get_all_companies(db: db_dependency):
    companies = db.query(Company).all()

    records = []
    for company in companies:
        record = CompanyModel(
            id=company.id,
            name=company.company_name,
            symbol=company.company_symbol

        )
        records.append(record)

    return CompanyListModel(companies=records)


@router.get('/company', status_code=status.HTTP_200_OK, response_model=CompanyModel)
async def get_company_by_id(id: int, db: db_dependency):
    company = db.query(Company).filter(Company.id == id).first()

    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    client = await get_influx_client()
    data = await client.query_data("30d", company.company_symbol)

    if data is None or data.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for company")

    record = CompanyModel(
        id=company.id,
        name=company.company_name,
        symbol=company.company_symbol,
        price_per_unit=data.iloc[-1]['ClosePrice']
    )
    return record


@router.post('/simulator', status_code=status.HTTP_200_OK, response_model=SimulatorResultModel)
async def run_simulator(db: db_dependency, company_list: SimulatorCompanyListModel):
    companies_values = {}
    for company in company_list.companies:
        companies_values[company.company_symbol] = company.investment_volume
    result = await get_metric(companies_values)

    return SimulatorResultModel(
        roi=result['ROI'],
        stddev=result['STDDEV'],
        interval=result['INTERVAL'],
        sharpe=result['SHARPE'],
        recommendation=result['RECOMMENDATION']
    )


@router.get('/user/wallet', response_model=List[WalletModel], status_code=status.HTTP_200_OK)
async def get_user_wallet(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user_id = user['id']

    user_transactions = (
        db.query(UserTransaction)
        .filter(UserTransaction.user_id == user_id)
        .all()
    )

    user_portfolio = {}
    for user_transaction in user_transactions:
        transaction = user_transaction.transaction
        company_name = transaction.company.company_name
        amount = transaction.amount
        price_per_unit = transaction.price_per_unit
        transaction_type = transaction.transaction_type

        if company_name not in user_portfolio:
            user_portfolio[company_name] = {'total_amount': 0, 'total_cost': 0, 'total_buy_amount': 0,
                                            'total_buy_cost': 0, 'total_sell_amount': 0, 'total_sell_cost': 0}

        if transaction_type == TransactionType.BUY:
            user_portfolio[company_name]['total_amount'] += amount
            user_portfolio[company_name]['total_buy_amount'] += amount
            user_portfolio[company_name]['total_buy_cost'] += amount * price_per_unit
        elif transaction_type == TransactionType.SELL:
            user_portfolio[company_name]['total_amount'] -= amount
            user_portfolio[company_name]['total_sell_amount'] += amount
            user_portfolio[company_name]['total_sell_cost'] += amount * price_per_unit
            user_portfolio[company_name]['total_buy_amount'] -= amount

    wallet_records = []
    for company_name, values in user_portfolio.items():
        total_amount = values['total_amount']
        total_buy_amount = values['total_buy_amount']
        total_buy_cost = values['total_buy_cost']
        total_sell_amount = values['total_sell_amount']
        total_sell_cost = values['total_sell_cost']

        average_buy_price = total_buy_cost / total_buy_amount if total_buy_amount > 0 else 0
        average_sell_price = total_sell_cost / total_sell_amount if total_sell_amount > 0 else 0

        wallet_record = WalletModel(
            name=company_name,
            amount=total_amount,
            average_buy_price=average_buy_price,
            average_sell_price=average_sell_price
        )
        wallet_records.append(wallet_record)

    return wallet_records
