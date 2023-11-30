from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import auth_controller
import authorization
import models
from authorization import validate_jwt
from database import SessionLocal, engine

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_controller.router)
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
user_dependency = Annotated[dict, Depends(validate_jwt)]

templates = Jinja2Templates(directory="templates")


@app.get("/me", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return {"User": user}


@app.get('/auth/register', response_class=HTMLResponse, include_in_schema=False)
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get('/auth/token', response_class=HTMLResponse, include_in_schema=False)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
