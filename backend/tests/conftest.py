import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.entities import AuthToken
from app.services.seed import seed_demo_data


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo_data(db)
    yield


@pytest.fixture
def client(prepare_database):
    with TestClient(app) as test_client:
        yield test_client
    with SessionLocal() as db:
        db.execute(delete(AuthToken))
        db.commit()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@123456"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
