from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any

class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Book title (required)")
    author: str = Field(..., min_length=1, max_length=50, description="Author name (required)")
    description: str = Field(..., min_length=10, max_length=1000, description="Book description")
    year: int = Field(..., ge=0, le=2100, description="Year of publication (between 0 and 2100)")

class User(BaseModel):
    username: str
    email: Optional[EmailStr] = None 
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None 


class UserInDB(User):
    hashed_password: str

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    disabled: Optional[bool] = None



class StandardResponse(BaseModel):
    success: bool
    message_key: str
    data: Optional[Any]
    errors: Optional[Any]

class StandardResponseWithData(StandardResponse):
    data: Any = Field(..., description="Response data")
    errors: Optional[Any] = None
class StandardResponseWithErrors(StandardResponse):
    data: Optional[Any] = None
    errors: Any = Field(..., description="Response errors")

class SurveyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None