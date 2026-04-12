from pydantic import BaseModel
from typing import List

class GenerateRequest(BaseModel):
    query: str
    context: List[str]

class GenerateResponse(BaseModel):
    answer: str