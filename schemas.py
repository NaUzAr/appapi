# app/schemas.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Any
from datetime import date, datetime

# Skema Respons Umum
class ResponseModel(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True  # Menambahkan konfigurasi ini jika diperlukan

# Skema untuk pengguna
class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str
    role: str
    disease: Optional[str] = None
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None

    class Config:
        from_attributes = True  # Untuk Pydantic v2

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    role: str
    disease: Optional[str] = None
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None

    class Config:
        from_attributes = True

# Skema untuk login
class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Username atau Email pengguna")
    password: str = Field(..., description="Password pengguna")

    @validator('identifier')
    def identifier_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Identifier tidak boleh kosong')
        return v

    @validator('password')
    def password_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Password tidak boleh kosong')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

# Skema untuk login dengan profil pengguna
class TokenResponse(ResponseModel):
    data: Optional[Any] = None  # Akan berisi token dan profil pengguna

    class Config:
        arbitrary_types_allowed = True  # Menambahkan konfigurasi ini jika diperlukan

# Skema untuk data entry
class DataEntryCreate(BaseModel):
    string_field1: str = Field(..., description="Sample String 1")
    string_field2: str = Field(..., description="Sample String 2")
    string_field3: str = Field(..., description="Sample String 3")
    int_field1: int = Field(..., description="Sample Integer 1")
    int_field2: int = Field(..., description="Sample Integer 2")
    int_field3: int = Field(..., description="Sample Integer 3")
    int_field4: int = Field(..., description="Sample Integer 4")
    int_field5: int = Field(..., description="Sample Integer 5")
    int_field6: int = Field(..., description="Sample Integer 6")
    int_field7: int = Field(..., description="Sample Integer 7")
    int_field8: int = Field(..., description="Sample Integer 8")

    class Config:
        from_attributes = True

class DataEntryUpdate(BaseModel):
    string_field1: Optional[str] = Field(None, description="Sample String 1")
    string_field2: Optional[str] = Field(None, description="Sample String 2")
    string_field3: Optional[str] = Field(None, description="Sample String 3")
    int_field1: Optional[int] = Field(None, description="Sample Integer 1")
    int_field2: Optional[int] = Field(None, description="Sample Integer 2")
    int_field3: Optional[int] = Field(None, description="Sample Integer 3")
    int_field4: Optional[int] = Field(None, description="Sample Integer 4")
    int_field5: Optional[int] = Field(None, description="Sample Integer 5")
    int_field6: Optional[int] = Field(None, description="Sample Integer 6")
    int_field7: Optional[int] = Field(None, description="Sample Integer 7")
    int_field8: Optional[int] = Field(None, description="Sample Integer 8")

    class Config:
        from_attributes = True

class DataEntryResponse(BaseModel):
    id: int
    string_field1: str
    string_field2: str
    string_field3: str
    int_field1: int
    int_field2: int
    int_field3: int
    int_field4: int
    int_field5: int
    int_field6: int
    int_field7: int
    int_field8: int
    owner_id: int

    class Config:
        from_attributes = True

# Skema untuk log aktivitas
class ActivityLogCreate(BaseModel):
    action: str

class ActivityLogResponse(BaseModel):
    id: int
    action: str
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True

# Skema untuk pembaruan profil pengguna
class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nama lengkap pengguna")
    email: Optional[EmailStr] = Field(None, description="Alamat email pengguna")
    current_password: Optional[str] = Field(None, description="Password saat ini pengguna")
    new_password: Optional[str] = Field(None, description="Password baru pengguna")
    username: Optional[str] = Field(None, description="Username baru pengguna")
    disease: Optional[str] = Field(None, description="Penyakit pengguna")
    date_of_birth: Optional[date] = Field(None, description="Tanggal lahir pengguna")
    place_of_birth: Optional[str] = Field(None, description="Tempat lahir pengguna")
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        if v is not None:
            if 'current_password' not in values or not values['current_password']:
                raise ValueError('Untuk mengganti password, current_password harus diberikan')
            if len(v) < 6:
                raise ValueError('Password baru harus memiliki setidaknya 6 karakter')
        return v

    class Config:
        from_attributes = True  # Menggunakan from_attributes untuk konsistensi dengan Pydantic v2

class UserReportCreate(BaseModel):
    int_value1: int
    int_value2: int
    int_value3: int
    int_value4: int
    int_value5: int
    int_value6: int
    int_value7: int
    int_value8: int

class UserReportResponse(BaseModel):
    id: int
    timestamp: datetime
    int_value1: int
    int_value2: int
    int_value3: int
    int_value4: int
    int_value5: int
    int_value6: int
    int_value7: int
    int_value8: int
    user_id: int

    class Config:
        from_attributes = True