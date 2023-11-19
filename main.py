from pydantic import BaseModel, Field
from models import Company
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends
import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine, checkfirst=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
