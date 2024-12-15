# app/main.py

from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from . import models, schemas, auth
from .database import engine
from sqlalchemy.orm import Session
from .dependencies import get_db
from .logging_service import log_activity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
import re

# Membuat semua tabel (gunakan Alembic di produksi)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API dengan Static Bearer Token dan JWT")

# Endpoint untuk registrasi pengguna baru
@app.post("/register", response_model=schemas.ResponseModel, dependencies=[Depends(auth.verify_static_token)])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Cek apakah username atau email sudah ada
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if existing_user:
        return schemas.ResponseModel(success=False, error="Username atau email sudah digunakan")
    
    hashed_password = auth.pwd_context.hash(user.password)
    db_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        disease=user.disease,
        date_of_birth=user.date_of_birth,
        place_of_birth=user.place_of_birth
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback()
        return schemas.ResponseModel(success=False, error="Username atau email sudah digunakan")
    
    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"User {db_user.email} telah mendaftar."
    )
    log_activity(db, activity_log, db_user.id)

    return schemas.ResponseModel(success=True, data=schemas.UserResponse.from_orm(db_user))

# Endpoint untuk login - Mengembalikan JWT token dan profil pengguna
@app.post("/login", response_model=schemas.TokenResponse, dependencies=[Depends(auth.verify_static_token)])
def login_for_access_token(form_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.identifier, form_data.password)
    if not user:
        return schemas.ResponseModel(success=False, error="Email atau password tidak valid")
    
    # Deteksi apakah identifier adalah email atau username
    if re.match(r'[^@]+@[^@]+\.[^@]+', form_data.identifier):
        sub = user.email
        action_identifier = user.email
    else:
        sub = user.username
        action_identifier = user.username

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": sub},
        expires_delta=access_token_expires
    )
    
    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"User {action_identifier} telah melakukan login."
    )
    log_activity(db, activity_log, user.id)

    # Menyusun data respons
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user_profile": schemas.UserResponse.from_orm(user)
    }

    return schemas.TokenResponse(success=True, data=response_data)

# Endpoint yang dilindungi menggunakan JWT
@app.get("/users/me/", response_model=schemas.ResponseModel)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    user_data = schemas.UserResponse.from_orm(current_user)
    return schemas.ResponseModel(success=True, data=user_data)

# Endpoint untuk memvalidasi token JWT
@app.get("/token/validate", response_model=schemas.ResponseModel)
def validate_token(current_user: models.User = Depends(auth.get_current_user)):
    # Jika token valid, current_user akan terisi
    return schemas.ResponseModel(success=True, data="Token is valid")

# Endpoint untuk membuat data entry baru
@app.post("/data_entries/", response_model=schemas.ResponseModel)
def create_data_entry(
    data_entry: schemas.DataEntryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_data_entry = models.DataEntry(
        string_field1=data_entry.string_field1,
        string_field2=data_entry.string_field2,
        string_field3=data_entry.string_field3,
        int_field1=data_entry.int_field1,
        int_field2=data_entry.int_field2,
        int_field3=data_entry.int_field3,
        int_field4=data_entry.int_field4,
        int_field5=data_entry.int_field5,
        int_field6=data_entry.int_field6,
        int_field7=data_entry.int_field7,
        int_field8=data_entry.int_field8,
        owner_id=current_user.id
    )
    db.add(new_data_entry)
    db.commit()
    db.refresh(new_data_entry)

    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"Created data entry with ID {new_data_entry.id}"
    )
    log_activity(db, activity_log, current_user.id)

    return schemas.ResponseModel(success=True, data=schemas.DataEntryResponse.from_orm(new_data_entry))

# Endpoint untuk mendapatkan semua data entry pengguna saat ini
@app.get("/data_entries/", response_model=schemas.ResponseModel)
def read_data_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    data_entries = db.query(models.DataEntry).filter(models.DataEntry.owner_id == current_user.id).offset(skip).limit(limit).all()

    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"Retrieved {len(data_entries)} data entries."
    )
    log_activity(db, activity_log, current_user.id)

    data_response = [schemas.DataEntryResponse.from_orm(entry) for entry in data_entries]
    return schemas.ResponseModel(success=True, data=data_response)

# Endpoint untuk mendapatkan data entry spesifik
@app.get("/data_entries/{data_entry_id}", response_model=schemas.ResponseModel)
def read_data_entry(
    data_entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    data_entry = db.query(models.DataEntry).filter(
        models.DataEntry.id == data_entry_id,
        models.DataEntry.owner_id == current_user.id
    ).first()
    if data_entry is None:
        return schemas.ResponseModel(success=False, error="Data entry tidak ditemukan")

    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"Retrieved data entry with ID {data_entry_id}"
    )
    log_activity(db, activity_log, current_user.id)

    return schemas.ResponseModel(success=True, data=schemas.DataEntryResponse.from_orm(data_entry))

# Endpoint untuk memperbarui data entry
@app.put("/data_entries/{data_entry_id}", response_model=schemas.ResponseModel)
def update_data_entry(
    data_entry_id: int,
    data_entry: schemas.DataEntryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_data_entry = db.query(models.DataEntry).filter(
        models.DataEntry.id == data_entry_id,
        models.DataEntry.owner_id == current_user.id
    ).first()
    if db_data_entry is None:
        return schemas.ResponseModel(success=False, error="Data entry tidak ditemukan")
    
    # Update field jika diberikan
    for field, value in data_entry.dict(exclude_unset=True).items():
        setattr(db_data_entry, field, value)
    
    db.commit()
    db.refresh(db_data_entry)

    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"Updated data entry with ID {data_entry_id}"
    )
    log_activity(db, activity_log, current_user.id)

    return schemas.ResponseModel(success=True, data=schemas.DataEntryResponse.from_orm(db_data_entry))

# Endpoint untuk menghapus data entry
@app.delete("/data_entries/{data_entry_id}", response_model=schemas.ResponseModel, status_code=status.HTTP_200_OK)
def delete_data_entry(
    data_entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_data_entry = db.query(models.DataEntry).filter(
        models.DataEntry.id == data_entry_id,
        models.DataEntry.owner_id == current_user.id
    ).first()
    if db_data_entry is None:
        return schemas.ResponseModel(success=False, error="Data entry tidak ditemukan")
    db.delete(db_data_entry)
    db.commit()

    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"Deleted data entry with ID {data_entry_id}"
    )
    log_activity(db, activity_log, current_user.id)

    return schemas.ResponseModel(success=True, data=None)

# Endpoint untuk memperbarui profil pengguna
@app.put("/users/me/profile", response_model=schemas.ResponseModel)
def update_user_profile(
    profile_update: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    
    # Jika pengguna ingin mengganti password
    if profile_update.new_password:
        if not auth.pwd_context.verify(profile_update.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Password saat ini tidak sesuai")
        # Hash password baru
        hashed_new_password = auth.pwd_context.hash(profile_update.new_password)
        user.hashed_password = hashed_new_password

    # Jika pengguna ingin mengganti email
    if profile_update.email and profile_update.email != user.email:
        existing_email_user = db.query(models.User).filter(models.User.email == profile_update.email).first()
        if existing_email_user:
            raise HTTPException(status_code=400, detail="Email sudah digunakan oleh pengguna lain")
        user.email = profile_update.email

    # Jika pengguna ingin mengganti username
    if profile_update.username and profile_update.username != user.username:
        existing_username_user = db.query(models.User).filter(models.User.username == profile_update.username).first()
        if existing_username_user:
            raise HTTPException(status_code=400, detail="Username sudah digunakan oleh pengguna lain")
        user.username = profile_update.username

    # Perbarui field lainnya jika diberikan
    if profile_update.name is not None:
        user.name = profile_update.name
    if profile_update.disease is not None:
        user.disease = profile_update.disease
    if profile_update.date_of_birth is not None:
        user.date_of_birth = profile_update.date_of_birth
    if profile_update.place_of_birth is not None:
        user.place_of_birth = profile_update.place_of_birth

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Terjadi kesalahan saat memperbarui profil")

    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"User {user.email} telah memperbarui profilnya."
    )
    log_activity(db, activity_log, user.id)
    
    return schemas.ResponseModel(success=True, data=schemas.UserResponse.from_orm(user))

# Endpoint untuk membuat log aktivitas (opsional, jika ingin membuat log secara manual)
@app.post("/logs/", response_model=schemas.ResponseModel)
def create_activity_log(
    log: schemas.ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    created_log = log_activity(db, log, current_user.id)
    return schemas.ResponseModel(success=True, data=schemas.ActivityLogResponse.from_orm(created_log))

# Endpoint untuk membaca log aktivitas pengguna
@app.get("/logs/", response_model=schemas.ResponseModel)
def read_activity_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    logs = db.query(models.ActivityLog)\
             .filter(models.ActivityLog.user_id == current_user.id)\
             .order_by(models.ActivityLog.timestamp.desc())\
             .offset(skip).limit(limit).all()

    # Log aktivitas
    activity_log = schemas.ActivityLogCreate(
        action=f"Retrieved {len(logs)} activity logs."
    )
    log_activity(db, activity_log, current_user.id)

    logs_response = [schemas.ActivityLogResponse.from_orm(log) for log in logs]
    return schemas.ResponseModel(success=True, data=logs_response)

# Endpoint untuk membaca log aktivitas menggunakan Static Bearer Token
@app.get("/logs/public", response_model=schemas.ResponseModel, dependencies=[Depends(auth.verify_static_token)])
def read_activity_logs_public(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    logs = db.query(models.ActivityLog)\
             .order_by(models.ActivityLog.timestamp.desc())\
             .offset(skip).limit(limit).all()

    logs_response = [schemas.ActivityLogResponse.from_orm(log) for log in logs]
    return schemas.ResponseModel(success=True, data=logs_response)

@app.post("/reports/", response_model=schemas.ResponseModel)
def create_report(
    report: schemas.UserReportCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_report = models.UserReport(
        int_value1=report.int_value1,
        int_value2=report.int_value2,
        int_value3=report.int_value3,
        int_value4=report.int_value4,
        int_value5=report.int_value5,
        int_value6=report.int_value6,
        int_value7=report.int_value7,
        int_value8=report.int_value8,
        user_id=current_user.id
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return schemas.ResponseModel(success=True, data=schemas.UserReportResponse.from_orm(db_report))

@app.get("/reports/", response_model=schemas.ResponseModel)
def get_user_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    reports = db.query(models.UserReport).filter(
        models.UserReport.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return schemas.ResponseModel(
        success=True, 
        data=[schemas.UserReportResponse.from_orm(r) for r in reports]
    )