from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import models
from controllers import user_controller, internal_controller, auth_controller
from authorization import validate_jwt
from database import engine
from utils import get_db

app = FastAPI()
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(internal_controller.router)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"])

models.Base.metadata.create_all(bind=engine, checkfirst=True)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]


@app.get("/me", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return {"User": user}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
