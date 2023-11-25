import uvicorn
from pydantic import BaseModel, Field
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends, status
import models
from typing import Annotated
from sqlalchemy.orm import Session
import auth

app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine, checkfirst=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)