import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status

from models import User

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import secrets

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
internal_auth_token = os.getenv('INTERNAL_AUTH_TOKEN')


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str
    
class ResetPasswordRequest(BaseModel):
    email: str

class ResetPasswordResponse(BaseModel):
    message: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return pwd_context.verify(password, hashed_pass)


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def validate_jwt(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')


async def validate_internal_auth(Authorization: str = Header()):
    if Authorization != internal_auth_token:
        raise HTTPException(status_code=400, detail="Unauthorized")


def validate_username(username: str):
    if len(username) < 3:
        return False
    if len(username) > 20:
        return False
    return True


def validate_password(password: str):
    if len(password) < 8:
        return False
    if len(password) > 40:
        return False
    return True


def validate_email(email: str):
    if len(email) < 5:
        return False
    if len(email) > 50:
        return False
    #todo regex
    return True


def get_user_by_email(email: str, db):
    return db.query(User).filter(User.email == email).first()


def generate_reset_code():
    return secrets.token_hex(8)


def send_email(to_email: str, reset_code: str):
    message = Mail(
        from_email=os.getenv('FROM_EMAIL'),
        to_emails=to_email,
        subject='Password reset',
        html_content=f'<strong>Reset code: {reset_code}</strong>'
    )
    
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Error sending email: {e}'
        )

def update_password(email: str, new_password: str, db):
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.password_hash = hash_password(new_password)
        db.commit()
        return True
    return False
