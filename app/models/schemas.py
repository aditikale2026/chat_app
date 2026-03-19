from  pydantic import BaseModel , Field
from typing import Any
class UploadResponse(BaseModel):
    answer: str
    filename: str
    upload_time:Any
    total_length:int
    
class RAGRequest(BaseModel):
    query:str = Field(
    json_schema_extra={"example": "What is AI?"}
)

class RAGResponse(BaseModel):
    query:str
    answer:str 
    mode:str    