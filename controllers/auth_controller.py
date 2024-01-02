from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

import authorization
from authorization import CreateUserRequest, hash_password, Token, authenticate_user, \
    create_access_token, ResetPasswordRequest, ResetPasswordResponse, generate_reset_code, \
    get_user_by_email, send_email, update_password
from models import User
from utils import get_db

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

db_dependency = Annotated[Session, Depends(get_db)]
password_reset_codes = {}

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(db: db_dependency,
                   create_user_request: CreateUserRequest):
    if not authorization.validate_username(create_user_request.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Username must be between 3 and 20 characters')
    if not authorization.validate_password(create_user_request.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Password must be between 8 and 20 characters')
    if not authorization.validate_email(create_user_request.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid email address')

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
    token = create_access_token(user.username, user.id, timedelta(minutes=6000))

    return {'access_token': token, 'token_type': 'bearer'}


@router.post("/forgot_password", response_model=ResetPasswordResponse)
async def forgot_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(request.email, db)
    if user:
        reset_code = generate_reset_code()

        password_reset_codes[reset_code] = request.email

        send_email(request.email, reset_code)

        return {"message": "Password reset instructions sent to your email."}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist.",
        )
        
@router.post("/reset_password", response_model=ResetPasswordResponse)
async def reset_password(code: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    email = password_reset_codes.get(code)
    if email:
        update_password(email, new_password, db)

        del password_reset_codes[code]

        return {"message": "Password reset successful."}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired reset code.",
        )
