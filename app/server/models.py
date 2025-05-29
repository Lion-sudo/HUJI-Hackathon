from pydantic import BaseModel
from typing import Optional, List, Dict

class Message(BaseModel):
    role: str
    content: str

class LLMRequest(BaseModel):
    prompt: str
    chat_history: Optional[List[Message]] = []
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000 