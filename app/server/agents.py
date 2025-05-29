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
    async def make_final_decision(self, evaluations: List[Dict], prompt: str) -> Dict:
        """
        Make a final decision based on all agent evaluations.
        Returns a dict with the verdict and explanation.
        """
        try:
            # Format evaluations for explanation
            evaluations_text = "\n\n".join([
                f"Evaluation from {eval['agent_name']} (weight: {eval['weight']}):\n{eval['evaluation']}"
                for eval in evaluations
            ])
            
            chat = self.model.start_chat(history=[])
            response = await asyncio.to_thread(
                chat.send_message,
                f"{self.config.system_prompt}\n\nOriginal prompt: {prompt}\n\nExpert evaluations:\n{evaluations_text}\n\nPlease provide your final verdict."
            )
            
            return {
                "verdict": response.text.strip()
            }
        except Exception as e:
            print(f"Error in Judge agent: {str(e)}")
            return {
                "verdict": "Error in final decision"
            }

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
    
    async def analyze_prompt(self, prompt: str) -> Dict:
        """
        Get evaluations from all agents and have the judge make a final decision.
        Returns a dict with the final verdict.
        """
        if not self.agents or not self.judge:
            return {"verdict": "No agents available"}
        
        # Get evaluations from all agents
        tasks = [agent.analyze_prompt(prompt) for agent in self.agents]
        evaluations = await asyncio.gather(*tasks)
        
        # Log each expert's evaluation
        for eval in evaluations:
            logger.info(f"Expert {eval['agent_name']} evaluation:\n{eval['evaluation']}")
        
        # Have the judge make the final decision
        final_decision = await self.judge.make_final_decision(evaluations, prompt)
        return final_decision 