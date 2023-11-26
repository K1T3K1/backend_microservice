import uvicorn
from pydantic import BaseModel, Field
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends, status
import models
from typing import Annotated
from sqlalchemy.orm import Session
import auth
from auth import get_current_user
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine, checkfirst=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/me", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return {"User": user}

@app.get('/auth/register', status_code=status.HTTP_200_OK, include_in_schema=False)
async def show_register_form():
    return FileResponse('templates/register.html')

@app.get('/auth/token', status_code=status.HTTP_200_OK, include_in_schema=False)
async def show_login_form():
    return FileResponse('templates/login.html')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)