from pydantic import BaseModel
from typing import Optional

class LLMRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000 