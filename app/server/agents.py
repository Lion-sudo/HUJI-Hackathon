from typing import List, Dict, Optional
import google.generativeai as genai
import asyncio
from dataclasses import dataclass
import json
from agent_prompts import get_prompt_for_council_member, get_prompt_for_council_leader, ADDED_PROMPT_DICT

@dataclass
class AgentConfig:
    name: str
    weight: float
    system_prompt: str
    api_key: str

class Agent:
    def __init__(self, config: AgentConfig, model):
        self.config = config
        self.model = model
        # self._setup_model()
    
    def _setup_model(self):
        # genai.configure(api_key=self.config.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        """
        try:
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
                "verdict": response.text.strip(),
                "confidence": self._extract_confidence(response.text)
            }
        except Exception as e:
            print(f"Error in Judge agent: {str(e)}")
            return {
                "verdict": "Error in final decision",
                "confidence": 0.0
            }
    
    def _extract_confidence(self, verdict_text: str) -> float:
        """
        Extract confidence score from the verdict text.
        Returns a value between 0 and 1.
        """
        try:
            # Look for confidence indicators in the text
            if "Not Permitted" in verdict_text:
                # If not permitted, look for strong language indicating high confidence
                if any(phrase in verdict_text.lower() for phrase in ["definitely", "clearly", "absolutely", "certainly"]):
                    return 0.9
                return 0.7
            elif "Permitted" in verdict_text:
                # If permitted, look for strong language indicating high confidence
                if any(phrase in verdict_text.lower() for phrase in ["definitely", "clearly", "absolutely", "certainly"]):
                    return 0.1
                return 0.3
            return 0.5  # Default to neutral confidence
        except:
            return 0.5

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
        Returns a dict with the final verdict and confidence score.
        """
        if not self.agents or not self.judge:
            return {"verdict": "No agents available", "confidence": 0.0}
        
        # Get evaluations from all agents
        tasks = [agent.analyze_prompt(prompt) for agent in self.agents]
        evaluations = await asyncio.gather(*tasks)
        
        # Have the judge make the final decision
        final_decision = await self.judge.make_final_decision(evaluations, prompt)
        return final_decision 