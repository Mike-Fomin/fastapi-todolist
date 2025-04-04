from requests.auth import HTTPBasicAuth
from sqlalchemy import MetaData
from sqlalchemy.sql.schema import Table

from app.database.database import User


def test_create_user(client, db_session):
    new_item = User(username="Test", password="test")
    db_session.add(new_item)
    db_session.commit()

    saved_item = db_session.query(User).filter_by(username="Test").first()
    assert saved_item is not None
    assert saved_item.username == "Test"
    assert saved_item.password == "test"


def test_register_user(client, db_session):
    user_data = {"username": "TestUser", "password": "testpassword"}
    response = client.post("/register", json=user_data)

    assert response.status_code == 200
    assert response.json() == {"message": "user added successfully"}

    saved_user = db_session.query(User).filter_by(username="TestUser").first()
    assert saved_user is not None
    assert saved_user.username == "TestUser"
    assert saved_user.check_password("testpassword")

    metadata = MetaData()
    metadata.reflect(bind=db_session.bind)
    assert f"{saved_user.username}_ToDoList" in metadata.tables


def test_crud_one_task(client, db_session):
    metadata = MetaData()
    metadata.reflect(bind=db_session.bind)

    test_table: Table = metadata.tables["TestUser_ToDoList"]

    request_data = {"title": "some title", "description": "some description"}

    wrong_auth = HTTPBasicAuth(username="TestUser", password="password")
    response = client.post("/item", json=request_data, auth=wrong_auth)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
    assert response.headers["WWW-Authenticate"] == "Basic"

    auth = HTTPBasicAuth(username="TestUser", password="testpassword")
    post_response = client.post("/item", json=request_data, auth=auth)

    assert post_response.status_code == 200
    assert post_response.json().get("title") == "some title"
    assert post_response.json().get("description") == "some description"
    assert post_response.json().get("done") == False

    db_value = db_session.execute(test_table.select()).first()
    db_values = db_session.execute(test_table.select()).fetchall()
    assert db_value.title == "some title"
    assert db_value.description == "some description"
    assert len(db_values) == 1

    wrong_put_response = client.put("/items/2", json={"title": "new title"}, auth=auth)

    assert wrong_put_response.status_code == 404
    assert wrong_put_response.json()["detail"] == "Элемент с номером id = 2 не найден"

    put_response = client.put("/items/1", json={"title": "new title"}, auth=auth)

    assert put_response.status_code == 200
    assert put_response.json()["title"] == "new title"

    wrong_del_response = client.delete("/items/3", auth=auth)

    assert wrong_del_response.status_code == 404
    assert wrong_del_response.json()["detail"] == "Элемент с номером id = 3 не найден"

    del_response = client.delete("/items/1", auth=auth)

    assert del_response.status_code == 200
    assert del_response.json()["message"] == "Элемент 1 удален"
