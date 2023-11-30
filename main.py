from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session

import authorization
import models
from authorization import validate_jwt
from database import SessionLocal, engine

app = FastAPI()
app.include_router(authorization.router)
models.Base.metadata.create_all(bind=engine, checkfirst=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]

@app.get("/me", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return {"User": user}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
