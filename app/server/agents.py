from typing import List, Dict, Optional
import google.generativeai as genai
import asyncio
from dataclasses import dataclass
import json
from agent_prompts import get_prompt_for_council_member, get_prompt_for_council_leader, ADDED_PROMPT_DICT
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    name: str
    weight: float
    system_prompt: str
    api_key: str

class Agent:
    def __init__(self, config: AgentConfig, model=None):
        self.config = config
        self.model = model or self._setup_model()
    
    def _setup_model(self):
        genai.configure(api_key=self.config.api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    
    async def analyze_prompt(self, prompt: str) -> Dict:
        """
        Analyze a prompt and return a structured response with the agent's evaluation.
        """
        try:
            chat = self.model.start_chat(history=[])
            response = await asyncio.to_thread(
                chat.send_message,
                f"{self.config.system_prompt}\n\nAnalyze this prompt: {prompt}\n\nProvide your evaluation in a clear and structured format."
            )
            
            return {
                "agent_name": self.config.name,
                "evaluation": response.text.strip(),
                "weight": self.config.weight
            }
        except Exception as e:
            print(f"Error in agent {self.config.name}: {str(e)}")
            return {
                "agent_name": self.config.name,
                "evaluation": "Error occurred during evaluation",
                "weight": self.config.weight
            }

class JudgeAgent(Agent):
    def __init__(self, config: AgentConfig, model=None, expert_agents: List[Agent] = None):
        super().__init__(config, model)
        self.expert_agents = expert_agents or []
    
    async def make_final_decision(self, prompt: str) -> Dict:
        """
        Make a final decision on the prompt, consulting experts only when needed.
        """
        try:
            # First, try to make a decision without consulting experts
            chat = self.model.start_chat(history=[])
            initial_response = await asyncio.to_thread(
                chat.send_message,
                f"{self.config.system_prompt}\n\nAnalyze this prompt: {prompt}\n\n"
                "First, try to make a decision on your own. If you're confident, provide your verdict. "
                "If you need expert input, respond with 'NEED_EXPERT_INPUT' followed by which experts you need "
                "and why (e.g., 'NEED_EXPERT_INPUT: lawyer for legal concerns, cybersecurity for potential exploits')."
            )
            
            # Check if expert input is needed
            if "NEED_EXPERT_INPUT" in initial_response.text:
                logger.info("Judge requested expert input")
                # Extract which experts are needed
                expert_types = self._parse_needed_experts(initial_response.text)
                
                # Get evaluations from needed experts
                expert_evals = []
                for expert in self.expert_agents:
                    if expert.config.name in expert_types:
                        logger.info(f"Consulting expert: {expert.config.name}")
                        eval_result = await expert.analyze_prompt(prompt)
                        expert_evals.append(eval_result)
                
                # Make final decision with expert input
                expert_text = "\n\n".join([
                    f"Evaluation from {eval['agent_name']}:\n{eval['evaluation']}"
                    for eval in expert_evals
                ])
                
                final_response = await asyncio.to_thread(
                    chat.send_message,
                    f"Based on the following expert evaluations:\n\n{expert_text}\n\n"
                    "Please provide your final verdict on the prompt."
                )
                
                return {
                    "verdict": final_response.text.strip(),
                    "used_experts": expert_types
                }
            else:
                # Use the initial decision if no expert input was needed
                return {
                    "verdict": initial_response.text.strip(),
                    "used_experts": []
                }
                
        except Exception as e:
            logger.error(f"Error in Judge agent: {str(e)}")
            return {
                "verdict": "Error in final decision",
                "used_experts": []
            }
    
    def _parse_needed_experts(self, response: str) -> List[str]:
        """
        Parse the judge's response to determine which experts are needed.
        """
        try:
            # Extract the part after NEED_EXPERT_INPUT
            expert_part = response.split("NEED_EXPERT_INPUT:")[1].strip()
            # Split by commas and extract expert types
            expert_types = []
            for part in expert_part.split(","):
                expert_type = part.split(" for ")[0].strip()
                if expert_type in [agent.config.name for agent in self.expert_agents]:
                    expert_types.append(expert_type)
            return expert_types
        except Exception as e:
            logger.error(f"Error parsing needed experts: {str(e)}")
            return []

class AgentManager:
    def __init__(self):
        self.agents: List[Agent] = []
        self.judge: Optional[JudgeAgent] = None
        self.total_weight: float = 0.0
    
    def add_agent(self, agent: Agent):
        self.agents.append(agent)
        self.total_weight += agent.config.weight
    
    def set_judge(self, judge: JudgeAgent):
        self.judge = judge
        # Pass all expert agents to the judge
        self.judge.expert_agents = self.agents
    
    async def analyze_prompt(self, prompt: str) -> Dict:
        """
        Have the judge analyze the prompt, consulting experts only when needed.
        """
        if not self.judge:
            return {"verdict": "No judge available"}
        
        # Let the judge make the decision
        final_decision = await self.judge.make_final_decision(prompt)
        
        # Log which experts were consulted
        if final_decision["used_experts"]:
            logger.info(f"Judge consulted experts: {', '.join(final_decision['used_experts'])}")
        else:
            logger.info("Judge made decision without consulting experts")
            
        return final_decision 