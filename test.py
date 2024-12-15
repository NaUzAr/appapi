# tests/test_main.py

import pytest
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from app import models, auth

import asyncio

@pytest.fixture(scope="module")
def anyio_backend():
    return 'asyncio'

@pytest.fixture(scope="module")
def test_db():
    # Membuat database test
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.mark.anyio
async def test_user_registration(client: AsyncClient, test_db: Session):
    response = await client.post("/register", json={
        "name": "Jane Doe",
        "username": "janedoe",
        "email": "janedoe@example.com",
        "role": "user",
        "disease": "None",
        "date_of_birth": "1992-02-02",
        "place_of_birth": "Town",
        "password": "securepassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "janedoe"
    assert data["email"] == "janedoe@example.com"

def get_token(test_db: Session, username: str, password: str) -> str:
    user = test_db.query(models.User).filter(models.User.username == username).first()
    assert user is not None
    token = auth.create_access_token(data={"sub": user.username})
    return token

@pytest.mark.anyio
async def test_user_login(client: AsyncClient, test_db: Session):
    # Registrasi terlebih dahulu
    await client.post("/register", json={
        "name": "John Smith",
        "username": "johnsmith",
        "email": "johnsmith@example.com",
        "role": "user",
        "disease": "None",
        "date_of_birth": "1985-05-05",
        "place_of_birth": "Village",
        "password": "anotherpassword"
    })

    response = await client.post("/login", json={
        "username": "johnsmith",
        "password": "anotherpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# ... Ubah endpoint lainnya sesuai penamaan baru
