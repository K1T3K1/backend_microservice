from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from authorization import CreateUserRequest, hash_password, Token, authenticate_user, \
    create_access_token
from database import SessionLocal
from models import User

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(db: db_dependency,
                   create_user_request: CreateUserRequest):
    create_user_model = User(
        username=create_user_request.username,
        password_hash=hash_password(create_user_request.password),
        email=create_user_request.email,
        last_login_date=datetime.now()
    )

    db.add(create_user_model)
    db.commit()

    return {'message': 'User registered successfully'}


@router.post('/token', response_model=Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                             db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate credentials')
    token = create_access_token(user.username, user.id, timedelta(minutes=60))

    return {'access_token': token, 'token_type': 'bearer'}
