from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str


#schema.py purpose
# Define the structure of API requests and responses.
# Validate incoming data.
# Control what data is returned to the client.
#it uses pydantic