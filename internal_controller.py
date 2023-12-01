from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql.annotation import Annotated

from database import SessionLocal

router = APIRouter(
    tags=['internal']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# class CreateUserRequest(BaseModel):
#     companies: map


# @router.post('/fill_db', status_code=status.HTTP_201_CREATED)
# async def register(db: db_dependency,
#                    create_user_request: CreateUserRequest):
#     for company in create_user_request.companies:
#         print(company)
#     return {'message': 'Worked'}