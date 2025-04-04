from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.selectable import Select

from app.api.authentication import authenticate_user, metadata
from app.database.database import User, create_session
from app.models.models import ToDoItemPy, UpgradeItemPy

router = APIRouter()


@router.post("/item")
def create_item(item: ToDoItemPy, db: Session = Depends(create_session), user: User = Depends(authenticate_user)):

    user_table: Table = metadata.tables[f"{user.username}_ToDoList"]
    stmt: Select = select(user_table).where(user_table.c.title==item.title and user_table.c.description==item.description)
    item_check: Row = db.execute(stmt).first()

    if not item_check:
        db.execute(user_table.insert().values(dict(title=item.title, description=item.description, done=item.done)))
        try:
            db.commit()
        except Exception as exx:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(exx)}")
        else:
            stmt: Select = select(user_table).where(
                user_table.c.title == item.title and user_table.c.description == item.description)
            new_item: Row = db.execute(stmt).first()
            return {
                "id": new_item.id,
                "title": new_item.title,
                "description": new_item.description,
                "done": new_item.done
            }
    raise HTTPException(status_code=401, detail="Такое задание уже есть в списке")


@router.get("/items/", response_model=list[ToDoItemPy])
def get_item_by_id(db: Session = Depends(create_session), user: User = Depends(authenticate_user)):

    user_table: Table = metadata.tables[f"{user.username}_ToDoList"]

    items: list[Row] = db.execute(user_table.select()).fetchall()
    if items:
        return items
    raise HTTPException(status_code=403, detail=f"Таблица пуста")


@router.get("/items/{item_id}")
def get_item_by_id(item_id: int, db: Session = Depends(create_session), user: User = Depends(authenticate_user)):

    user_table: Table = metadata.tables[f"{user.username}_ToDoList"]
    stmt: Select = select(user_table).where(user_table.c.id==item_id)
    item_check: Row = db.execute(stmt).first()

    if item_check:
        return {
            "id": item_check.id,
            "title": item_check.title,
            "description": item_check.description,
            "done": item_check.done
        }
    raise HTTPException(status_code=404, detail=f"Элемент с номером id = {item_id} не найден")


@router.put('/items/{item_id}')
def make_changes(
        item_id: int,
        item: UpgradeItemPy,
        db: Session = Depends(create_session),
        user: User = Depends(authenticate_user)
):

    user_table: Table = metadata.tables[f"{user.username}_ToDoList"]
    stmt: Select = select(user_table).where(user_table.c.id == item_id)
    item_check: Row = db.execute(stmt).first()

    if not item_check:
        raise HTTPException(status_code=404, detail=f"Элемент с номером id = {item_id} не найден")

    update_data: dict = {}
    if item.title is not None:
        update_data["title"] = item.title
    if item.description is not None:
        update_data["description"] = item.description
    if item.done is not None:
        update_data["done"] = item.done

    if not update_data:
        return item_check._asdict()

    update_stmt = user_table.update().where(user_table.c.id == item_id).values(**update_data)

    try:
        db.execute(update_stmt)
        db.commit()
    except Exception as exx:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(exx)}")
    else:
        item_check: Row = db.execute(stmt).first()
        return {
            "id": item_check.id,
            "title": item_check.title,
            "description": item_check.description,
            "done": item_check.done
        }


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(create_session), user: User = Depends(authenticate_user)):

    user_table: Table = metadata.tables[f"{user.username}_ToDoList"]
    stmt: Select = select(user_table).where(user_table.c.id == item_id)
    item_check: Row = db.execute(stmt).first()

    if not item_check:
        raise HTTPException(status_code=404, detail=f"Элемент с номером id = {item_id} не найден")

    try:
        del_stmt = user_table.delete().where(user_table.c.id == item_id)
        db.execute(del_stmt)
        db.commit()
    except Exception as exx:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(exx)}")
    else:
        return {"message": f"Элемент {item_id} удален"}
