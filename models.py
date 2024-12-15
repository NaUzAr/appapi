# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Pastikan tipe data ini VARCHAR
    disease = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    place_of_birth = Column(String, nullable=True)

    data_entries = relationship("DataEntry", back_populates="owner")
    activity_logs = relationship("ActivityLog", back_populates="user")
    reports = relationship("UserReport", back_populates="user")

class DataEntry(Base):
    __tablename__ = "data_entries"

    id = Column(Integer, primary_key=True, index=True)
    string_field1 = Column(String, nullable=False)
    string_field2 = Column(String, nullable=False)
    string_field3 = Column(String, nullable=False)
    int_field1 = Column(Integer, nullable=False)
    int_field2 = Column(Integer, nullable=False)
    int_field3 = Column(Integer, nullable=False)
    int_field4 = Column(Integer, nullable=False)
    int_field5 = Column(Integer, nullable=False)
    int_field6 = Column(Integer, nullable=False)
    int_field7 = Column(Integer, nullable=False)
    int_field8 = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="data_entries")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="activity_logs")

class UserReport(Base):
    __tablename__ = "user_reports"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    int_value1 = Column(Integer, nullable=False)
    int_value2 = Column(Integer, nullable=False)
    int_value3 = Column(Integer, nullable=False) 
    int_value4 = Column(Integer, nullable=False)
    int_value5 = Column(Integer, nullable=False)
    int_value6 = Column(Integer, nullable=False) 
    int_value7 = Column(Integer, nullable=False)
    int_value8 = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="reports")