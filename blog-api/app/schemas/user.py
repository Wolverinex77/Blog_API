from app.utils import validators
from pydantic import BaseModel,field_validator,Field,EmailStr
from typing import Optional
from app.models.user import UserRole
class UserCreate(BaseModel):
    username:str=Field(max_length=50)
    email:EmailStr
    password:str
    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        return validators.validate_password(value)
    bio:Optional[str] = None
    avatar_url:Optional[str] = None
    is_active:bool = True
class UserLogin(BaseModel):
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

class UpdateProfile(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        if value is None:
            return value
        return validators.validate_password(value)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role:str
    bio:Optional[str] = None
    avatar_url:Optional[str] = None
    is_active:bool
    model_config = {
        "from_attributes": True
    }