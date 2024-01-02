import os
from typing import Annotated

from fastapi import APIRouter
from fastapi import Request
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from models import Company
from utils import get_db
from authorization import validate_internal_auth

router = APIRouter(
    tags=['internal'],
    dependencies=[Depends(validate_internal_auth)]
)

db_dependency = Annotated[Session, Depends(get_db)]


class CompanyModel(BaseModel):
    name: str
    symbol: str


class CompanyListModel(BaseModel):
    companies: list[CompanyModel]


class InternalResponse(BaseModel):
    status: str


# todo: add authentication
@router.post('/append_companies', status_code=status.HTTP_201_CREATED, response_model=InternalResponse)
async def append_companies(db: db_dependency,
                           company_list: CompanyListModel):
    # auth_header = request.headers.get('Authorization')
    # if auth_header is not internal_auth_token:
    #     return {'status': 'failed'}

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
