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


from pydantic import BaseModel, Field, model_validator


class ChangePassword(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=12)

    @model_validator(mode="after")
    def validate_new_password(self):
        if self.current_password == self.new_password:
            raise ValueError(
                "New password must be different from current password."
            )

        if self.new_password.strip() != self.new_password:
            raise ValueError(
                "New password must not start or end with whitespace."
            )

        if len(self.new_password.encode("utf-8")) > 72:
            raise ValueError(
                "New password must not exceed 72 UTF-8 bytes."
            )

        return self