import json
import re
from typing import Dict, Any, List
from app.llm.client import llm_client
from app.llm.prompts import ROUTER_SYSTEM_PROMPT

class AgentRouter:
    def __init__(self):
        self.llm = llm_client
    
    def route(self, question: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        profile_context = ""
        if user_profile:
            profile_context = f"\nUser context: Age {user_profile.get('age')}, Income ${user_profile.get('income', 0):,}"
        
        messages = [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}{profile_context}"}
        ]
        
        raw_response = self.llm.generate(messages, temperature=0.0, max_tokens=512, json_mode=True)
        
        try:
            plan = self._extract_json(raw_response)
            if not self._validate_plan(plan):
                return self._fallback_plan()
            return plan
        except Exception as e:
            print(f"Router error: {e}, using fallback")
            return self._fallback_plan()
    
    def _extract_json(self, text: str) -> dict:
        if not text or not isinstance(text, str):
            raise ValueError("Empty model output")
        
        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)
        
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found")
        
        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    json_str = text[start:i+1]
                    return json.loads(json_str)
        
        raise ValueError("No valid JSON object could be parsed")
    
    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        if "modules" not in plan or not isinstance(plan["modules"], list):
            return False
        if len(plan["modules"]) == 0:
            return False
        
        valid_modules = ["tax_optimization", "investment_allocation", "estate_planning"]
        for module in plan["modules"]:
            if module not in valid_modules:
                return False
        
        return True
    
    def _fallback_plan(self) -> Dict[str, Any]:
        return {
            "modules": ["tax_optimization", "investment_allocation", "estate_planning"],
            "reasoning": "Comprehensive analysis across all domains"
        }

router = AgentRouter()
