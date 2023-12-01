from typing import Annotated, Optional

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from starlette import status

from database import SessionLocal
from models import Company
from utils import get_db

router = APIRouter(
    tags=['internal']
)

db_dependency = Annotated[Session, Depends(get_db)]


class CompanyModel(BaseModel):
    name: str
    symbol: str


class CompanyListModel(BaseModel):
    companies: list[CompanyModel]


class InternalResponse(BaseModel):
    status: str


#todo: add authentication
@router.post('/append_companies', status_code=status.HTTP_201_CREATED, response_model=InternalResponse)
async def register(db: db_dependency,
                   company_list: CompanyListModel):
    companies = []
    for company in company_list.companies:
        company = Company(
            company_name=company.name,
            company_symbol=company.symbol
        )
        companies.append(company)

    db.add_all(companies)
    db.commit()

    return {'status': 'success'}
