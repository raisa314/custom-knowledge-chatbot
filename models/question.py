from pydantic import BaseModel
from typing import Any

class Question(BaseModel):
    question: str
    session_id: str