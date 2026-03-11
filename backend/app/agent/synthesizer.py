from typing import Dict, Any, List
import json
from app.llm.client import llm_client
from app.llm.prompts import SYNTHESIZER_SYSTEM_PROMPT, RISK_DISCLAIMER

class RecommendationSynthesizer:
    def __init__(self):
        self.llm = llm_client
    
    def synthesize(
        self,
        question: str,
        module_results: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        context_blocks = []
        all_evidence = []
        
        for result in module_results:
            module_name = result.get("module", "unknown")
            analysis = result.get("analysis", "")
            evidence = result.get("evidence", [])
            
            context_blocks.append(f"=== {module_name.upper().replace('_', ' ')} ===\n{analysis}")
            all_evidence.extend(evidence)
        
        combined_context = "\n\n".join(context_blocks)
        
        profile_summary = f"""
Age: {user_profile.get('age')}, Income: ${user_profile.get('income', 0):,}
Assets: {user_profile.get('assets', {})}
Family: {user_profile.get('family', {})}
Goals: {user_profile.get('goals', [])}
"""
        
        messages = [
            {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
User Profile:
{profile_summary}

Question: {question}

Module Analyses:
{combined_context}

Synthesize a comprehensive, integrated recommendation that:
1. Addresses the user's question directly
2. Highlights key insights from each relevant module
3. Explains interdependencies (e.g., how tax strategy affects investment choices)
4. Provides actionable next steps
5. Cites all sources using [doc_id]

Format your response with clear sections and bullet points.
"""}
        ]
        
        final_recommendation = self.llm.generate(messages, temperature=0.4, max_tokens=8192)
        
        final_recommendation += RISK_DISCLAIMER
        
        breakdown = self._create_breakdown(module_results)
        
        return {
            "recommendation": final_recommendation,
            "breakdown": breakdown,
            "evidence": all_evidence,
            "modules_used": [r["module"] for r in module_results]
        }
    
    def _create_breakdown(self, module_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        breakdown = {}
        
        for result in module_results:
            module = result.get("module")
            
            if module == "tax_optimization":
                breakdown["tax"] = {
                    "strategies": result.get("strategies", []),
                    "key_considerations": result.get("key_considerations", [])
                }
            
            elif module == "investment_allocation":
                breakdown["investment"] = {
                    "risk_profile": result.get("risk_profile", "N/A"),
                    "allocation": result.get("recommended_allocation", {}),
                    "tax_efficiency_score": result.get("tax_efficiency_score", 0)
                }
            
            elif module == "estate_planning":
                breakdown["estate"] = {
                    "estate_value": result.get("estate_value", 0),
                    "triggers": result.get("planning_triggers", []),
                    "structures": result.get("recommended_structures", [])
                }
        
        return breakdown

synthesizer = RecommendationSynthesizer()
