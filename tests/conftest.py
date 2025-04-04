import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.database import Base, create_session
from main import app


@pytest.fixture(scope='module')
def test_db():
    engine = create_engine("sqlite:///tests/test.db", echo=False, poolclass=NullPool)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(test_db):
    session_factory = sessionmaker(bind=test_db)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):

    def override_create_session():
        yield db_session

    app.dependency_overrides[create_session] = override_create_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()