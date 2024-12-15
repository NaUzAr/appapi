# app/dependencies.py

from .database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
