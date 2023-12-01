from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status

from authorization import validate_jwt
from utils import get_db


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]

router = APIRouter(
    tags=['user']
)

class TestAction(BaseModel):
    access_token: str
    token_type: str


@router.delete('/user/transaction', status_code=status.HTTP_200_OK, response_model=TestAction)
async def delete_transaction(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return {'message': 'Worked'}