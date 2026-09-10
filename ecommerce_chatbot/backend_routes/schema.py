from pydantic import BaseModel,EmailStr
from typing import Tuple,Optional
from datetime import datetime

class ChatRequest(BaseModel):
    query : str

class ChatResponse(BaseModel):
    response: str

class CreateUserIn(BaseModel):
    email_id : EmailStr
    password : str

class CreateUserOut(BaseModel):
    email_id : EmailStr
    created_at : datetime
    id : int
    
    class Config:
        from_attributes = True

class Userlogin(BaseModel):
    email_id : EmailStr
    password : str

class UserloginOut(BaseModel):
    email_id : EmailStr
    password : str

class TokenData(BaseModel):
    id : int

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class UpdatePswd:
    email_id = EmailStr
    new_password : Optional[str]
    otp : Optional[int] 
    
class ForgotPasswordIn(BaseModel):
    email_id: EmailStr

class UpdatePswd(BaseModel):
    email_id: EmailStr
    otp: str
    new_password: str

class VerifyAccountOTP(BaseModel):
    email_id: EmailStr
    otp: str