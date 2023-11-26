from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from auth import get_hashed_password, create_access_token
from sqlalchemy.orm import Session
from database import SessionLocal, engine

app = FastAPI()
