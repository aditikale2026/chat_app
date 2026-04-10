from pydantic import basemodel
from typing import Literal

class UserCreate(basemodel):
    username:str
    password:str
    role:Literal['admin','user','viewer']='user'
    
class UserInDatabase(basemodel):
    username:str
    hashed_password:str
    role:str
    
class TokenResponse(basemodel):
    access_token:str
    token_type:str = 'bearer'
    
    
    
            