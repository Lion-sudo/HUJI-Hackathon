from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import re
import json
from models import LLMRequest

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_jailbreak_attempt(prompt: str) -> bool:
    """
    Simple jailbreak detection - can be enhanced with more sophisticated checks
    """
    # List of common jailbreak patterns
    jailbreak_patterns = [
        r"ignore.*previous.*instructions",
        r"you.*are.*now.*(?:dan|jailbreak|unrestricted)",
        r"bypass.*restrictions",
        r"ignore.*ethical",
        r"you.*can.*do.*anything",
        r"you.*are.*not.*bound",
        r"you.*are.*not.*an.*ai",
        r"you.*are.*not.*a.*language.*model",
    ]
    
    prompt_lower = prompt.lower()
    return any(re.search(pattern, prompt_lower) for pattern in jailbreak_patterns)

@app.middleware("http")
async def jailbreak_middleware(request: Request, call_next):
    if request.url.path == "/api/chat" and request.method == "POST":
        body = await request.body()
        try:
            data = json.loads(body)
            if "prompt" in data and is_jailbreak_attempt(data["prompt"]):
                raise HTTPException(status_code=403, detail="Jailbreak attempt detected")
        except json.JSONDecodeError:
            pass
    response = await call_next(request)
    return response

@app.post("/api/chat")
async def chat(request: LLMRequest):
    # TODO: Implement actual LLM call here
    # This is a stub response
    return {
        "response": "This is a stub response. LLM integration pending.",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 