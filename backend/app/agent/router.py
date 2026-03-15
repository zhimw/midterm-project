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
        
        raw_response = self.llm.generate(messages, temperature=0.0, max_tokens=1024, json_mode=True, disable_thinking=True)
        
        try:
            plan = self._extract_json(raw_response)
            if not self._validate_plan(plan):
                print(f"Router warning: invalid plan structure from model: {plan}")
                return self._fallback_plan()
            return plan
        except Exception as e:
            preview = raw_response if isinstance(raw_response, str) else str(raw_response)
            preview = preview[:500].replace("\n", " ")
            print(f"Router error: {e}. Raw router response preview: {preview}. Using fallback plan.")
            return self._fallback_plan()
    
    def _extract_json(self, text: str) -> dict:
        if not text or not isinstance(text, str):
            raise ValueError("Empty model output")
        
        # Strip common markdown fences (opening and closing)
        text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text.strip())
        text = text.strip()
        
        # First, try to parse the whole string directly
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # If that fails, try to find the JSON object that contains "modules"
        match = re.search(r"\{[\s\S]*?\"modules\"[\s\S]*?\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Try to recover from truncated JSON: extract "modules": ["a", "b", ...]
        modules = self._extract_modules_from_truncated(text)
        if modules:
            return {"modules": modules, "reasoning": "Recovered from truncated router response"}
        
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
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        break
        # Last resort: try truncated extraction again on the substring we have
        modules = self._extract_modules_from_truncated(text[start:])
        if modules:
            return {"modules": modules, "reasoning": "Recovered from truncated router response"}
        
        raise ValueError("No valid JSON object could be parsed")
    
    def _extract_modules_from_truncated(self, text: str) -> List[str]:
        """Extract module names from truncated JSON like '"modules": ["tax_optimization"'."""
        valid = {"tax_optimization", "investment_allocation", "estate_planning"}
        # Find "modules": [ ... ] - allow incomplete closing
        m = re.search(r'"modules"\s*:\s*\[([\s\S]*?)(?:\]|$)', text)
        if not m:
            return []
        inner = m.group(1)
        # Extract quoted module names
        found = re.findall(r'"([a-z_]+)"', inner)
        return [x for x in found if x in valid]
    
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
