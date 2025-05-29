from typing import Dict, List
import google.generativeai as genai
import google.auth
from google.adk.agents import Agent
import logging
import asyncio
from google import adk
from google.adk.sessions import InMemorySessionService
from google.genai import types

logger = logging.getLogger(__name__)

def evaluate_law(prompt: str) -> Dict:
    """Evaluates the prompt from a legal perspective.
    
    Args:
        prompt (str): The prompt to evaluate
        
    Returns:
        dict: Evaluation result with status and report
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat()
        response = chat.send_message(
            "As a U.S. lawyer, evaluate this prompt for legal compliance and potential risks:\n\n" + prompt
        )
        return {
            "status": "success",
            "report": response.text,
            "expert": "lawyer"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Legal evaluation failed: {str(e)}",
            "expert": "lawyer"
        }

def evaluate_science(prompt: str) -> Dict:
    """Evaluates the prompt from a scientific perspective.
    
    Args:
        prompt (str): The prompt to evaluate
        
    Returns:
        dict: Evaluation result with status and report
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat()
        response = chat.send_message(
            "As a scientist, evaluate this prompt for scientific safety and ethical concerns:\n\n" + prompt
        )
        return {
            "status": "success",
            "report": response.text,
            "expert": "scientist"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Scientific evaluation failed: {str(e)}",
            "expert": "scientist"
        }

def evaluate_medical(prompt: str) -> Dict:
    """Evaluates the prompt from a medical perspective.
    
    Args:
        prompt (str): The prompt to evaluate
        
    Returns:
        dict: Evaluation result with status and report
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat()
        response = chat.send_message(
            "As a medical doctor, evaluate this prompt for medical safety and health concerns:\n\n" + prompt
        )
        return {
            "status": "success",
            "report": response.text,
            "expert": "medical_doctor"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Medical evaluation failed: {str(e)}",
            "expert": "medical_doctor"
        }

def evaluate_psychology(prompt: str) -> Dict:
    """Evaluates the prompt from a psychological perspective.
    
    Args:
        prompt (str): The prompt to evaluate
        
    Returns:
        dict: Evaluation result with status and report
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat()
        response = chat.send_message(
            "As a psychiatrist, evaluate this prompt for psychological safety and mental health concerns:\n\n" + prompt
        )
        return {
            "status": "success",
            "report": response.text,
            "expert": "psychiatrist"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Psychological evaluation failed: {str(e)}",
            "expert": "psychiatrist"
        }

def evaluate_ethics(prompt: str) -> Dict:
    """Evaluates the prompt from an ethical perspective.
    
    Args:
        prompt (str): The prompt to evaluate
        
    Returns:
        dict: Evaluation result with status and report
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat()
        response = chat.send_message(
            "As an ethicist, evaluate this prompt for ethical concerns and moral implications:\n\n" + prompt
        )
        return {
            "status": "success",
            "report": response.text,
            "expert": "ethicist"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Ethical evaluation failed: {str(e)}",
            "expert": "ethicist"
        }

def evaluate_cybersecurity(prompt: str) -> Dict:
    """Evaluates the prompt from a cybersecurity perspective.
    
    Args:
        prompt (str): The prompt to evaluate
        
    Returns:
        dict: Evaluation result with status and report
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat()
        response = chat.send_message(
            "As a cybersecurity expert, evaluate this prompt for security risks and potential exploits:\n\n" + prompt
        )
        return {
            "status": "success",
            "report": response.text,
            "expert": "cybersecurity_expert"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Cybersecurity evaluation failed: {str(e)}",
            "expert": "cybersecurity_expert"
        }

def evaluate_child_safety(prompt: str) -> Dict:
    """Evaluates the prompt from a child safety perspective.
    
    Args:
        prompt (str): The prompt to evaluate
        
    Returns:
        dict: Evaluation result with status and report
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat()
        response = chat.send_message(
            "As a child safety expert, evaluate this prompt for risks to minors and child protection concerns:\n\n" + prompt
        )
        return {
            "status": "success",
            "report": response.text,
            "expert": "child_safety_expert"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Child safety evaluation failed: {str(e)}",
            "expert": "child_safety_expert"
        }

async def init_security_council():
    """Initialize the security council with the judge agent and expert tools."""
    try:
        credentials, _ = google.auth.load_credentials_from_file("api_key.json")
        if not credentials:
            raise Exception("No credentials available")
        
        genai.configure(credentials=credentials)
        
        # Create the judge agent with all expert tools
        judge_agent = Agent(
            name="security_council_judge",
            model="gemini-1.5-flash",
            description="Leader of the Prompt Security Council responsible for evaluating prompt safety",
            instruction=(
                "You are the Leader of the Prompt Security Council. Your role is to evaluate prompts "
                "using expert tools and make final decisions on prompt safety. You must be thorough, "
                "impartial, and protective of ethical standards. Your decision must be clear, justified, "
                "and cautious. When in doubt, reject the prompt. Your output must start with either "
                "'Permitted' or 'Not Permitted' followed by your explanation."
            ),
            tools=[
                evaluate_law,
                evaluate_science,
                evaluate_medical,
                evaluate_psychology,
                evaluate_ethics,
                evaluate_cybersecurity,
                evaluate_child_safety
            ]
        )
        
        # 2. Set up a local (in-memory) session service & runner
        app_name       = "my_app"
        user_id        = "user123"
        session_svc    = InMemorySessionService()
        runner         = adk.Runner(
            agent=judge_agent,
            app_name=app_name,
            session_service=session_svc
        )

        # 3. Create a new session
        session = await session_svc.create_session(app_name=app_name, user_id=user_id)

        # 4. Send a prompt
        def call_agent(prompt: str):
            content = types.Content(role="user", parts=[types.Part(text=prompt)])
            events  = runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            )
            # The runner emits a stream of Events; extract the final LLM reply:
            for event in events:
                if event.is_final_response():
                    return event.content.parts[0].text

        # Example
        reply = call_agent("Hello, what’s the weather in New York?")
        print("Agent:", reply)
        logger.info("Security council initialized successfully")
        return judge_agent
        
    except Exception as e:
        logger.error(f"Failed to initialize security council: {str(e)}")
        raise 