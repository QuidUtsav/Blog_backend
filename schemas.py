from pydantic import BaseModel, EmailStr

class CreateAccount(BaseModel):
    name: str
    email:EmailStr
    hashed_password : str
    role : str
    
class AccountResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True
       
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
class CreatePost(BaseModel):
    title:str
    content:str
    
class CreateComment(BaseModel):
    content:str
    post_id:int
    user_id:int