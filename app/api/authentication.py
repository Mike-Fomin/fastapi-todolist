from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import Boolean, Column, Integer, String, Table
from sqlalchemy.orm import Session

from app.database.database import Base, User, create_session, engine
from app.models.models import UserPy

metadata = Base.metadata
metadata.reflect(bind=engine)


security = HTTPBasic()

auth_router = APIRouter()


@auth_router.post("/register", response_model=dict)
def auth_user(user: UserPy, db: Session = Depends(create_session)):
    user_check: User | None = db.query(User).filter_by(username=user.username).first()
    if user_check is None:
        new_user = User(username=user.username)
        new_user.set_password(user.password)
        db.add(new_user)
        try:
            db.commit()
        except Exception as exx:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(exx)}")
        else:
            Table(
                f"{new_user.username}_ToDoList",
                metadata,
                Column("id", Integer, primary_key=True),
                Column("title", String(50), nullable=False),
                Column("description", String),
                Column("done", Boolean, default=False),
            )
            metadata.create_all(bind=db.bind)
            return {"message": "user added successfully"}
    raise HTTPException(status_code=401, detail="User is already exists")


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(create_session)):
    user_check: User = db.query(User).filter_by(username=credentials.username).first()
    if user_check is not None and user_check.check_password(credentials.password):
        return user_check
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )

