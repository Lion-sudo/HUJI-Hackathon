from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import LLMRequest
from agents import AgentManager, Agent, JudgeAgent, AgentConfig
from agent_prompts import get_prompt_for_council_member, get_prompt_for_council_leader, ADDED_PROMPT_DICT
import logging
import uuid
import google.generativeai as genai
import google.auth
import asyncio
from contextlib import asynccontextmanager

API_KEY_FILE = "api_key.json"
# Configure the risk threshold (0.0 to 1.0)
RISK_THRESHOLD = 0.7  # Reject prompts with risk score >= 0.7

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Global Gemini model instance
gemini_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up server...")
    global gemini_model
    gemini_model = init_gemini()
    load_agents()  # Uncomment this to load the council of agents
    logger.info("Server startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down server...")
    # Add any cleanup code here if needed
    logger.info("Server shutdown complete")

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent manager
agent_manager = AgentManager()

# Initialize Gemini model
def init_gemini():
    try:
        credentials, _ = google.auth.load_credentials_from_file("api_key.json")
        if not credentials:
            raise Exception("No credentials available")
        
        genai.configure(credentials=credentials)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Successfully initialized Gemini model")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {str(e)}")
        return None

# Load agent configurations
def load_agents():
    credentials, _ = google.auth.load_credentials_from_file("api_key.json")
    if not credentials:
        raise Exception("No credentials available")
    
    logger.info("Initializing agents...")
    
    # Create the judge agent first
    judge_config = AgentConfig(
        name="judge",
        weight=1.0,
        system_prompt=get_prompt_for_council_leader(),
        api_key=credentials
    )
    judge = JudgeAgent(judge_config, gemini_model)
    agent_manager.set_judge(judge)
    logger.info("Judge agent initialized")
    
    # Create expert agents
    expert_weights = {
        "lawyer": 1.0,
        "scientist": 0.9,
        "medical_doctor": 1.0,
        "psychiatrist": 0.9,
        "ethicist": 1.0,
        "cybersecurity_expert": 1.0,
        "child_safety_expert": 1.0
    }
    
    for expert_type, weight in expert_weights.items():
        try:
            expert_prompt = get_prompt_for_council_member(expert_type)
            config = AgentConfig(
                name=expert_type,
                weight=weight,
                system_prompt=expert_prompt,
                api_key=credentials
            )
            agent_manager.add_agent(Agent(config, gemini_model))
            logger.info(f"Added {expert_type} agent with weight {weight}")
        except ValueError as e:
            logger.error(f"Failed to create {expert_type} agent: {str(e)}")
    
    logger.info(f"Total agents initialized: {len(agent_manager.agents) + 1} (including judge)")

@app.post("/api/chat")
async def chat(request: LLMRequest):
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Processing chat request")
    
    if not gemini_model:
        logger.error(f"[{request_id}] Gemini model not initialized")
        raise HTTPException(status_code=500, detail="AI model not initialized")
    
    try:
        # First, have the council evaluate the prompt
        logger.info(f"[{request_id}] Having council evaluate prompt")
        council_decision = await agent_manager.analyze_prompt(request.prompt)
        
        # Log the council's decision
        logger.info(f"[{request_id}] Council decision:\n{council_decision['verdict']}")
        
        # Check if the prompt was permitted
        if "Not Permitted" in council_decision["verdict"]:
            logger.warning(f"[{request_id}] Council rejected prompt: {council_decision['verdict']}")
            raise HTTPException(
                status_code=403,
                detail="Request rejected by security council"
            )
        
        # If permitted, proceed with the chat
        logger.info(f"[{request_id}] Council approved prompt, proceeding with chat")
        chat = gemini_model.start_chat()
        
        # Convert chat history to Gemini format and send previous messages
        for message in request.chat_history:
            await asyncio.to_thread(
                chat.send_message,
                message.content
            )
        
        # Send the current message and get response
        logger.info(f"[{request_id}] Sending prompt to Gemini: {request.prompt[:100]}...")
        response = await asyncio.to_thread(
            chat.send_message,
            request.prompt
        )
        
        logger.info(f"[{request_id}] Received response from Gemini")
        return {
            "response": response.text,
            "status": "success",
            "council_verdict": council_decision["verdict"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error in chat processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)