import uvicorn
from pydantic import BaseModel, Field

import api_controller
from models import Company
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends
from flask_sqlalchemy import SQLAlchemy
import models

app = api_controller.app
models.Base.metadata.create_all(bind=engine, checkfirst=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)