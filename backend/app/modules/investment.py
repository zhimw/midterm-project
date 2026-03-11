from typing import Dict, Any, List
from app.llm.client import llm_client
from app.llm.prompts import INVESTMENT_REASONING_PROMPT
from app.rag.retriever import rag_retriever

class InvestmentAllocationModule:
    def __init__(self):
        self.llm = llm_client
        self.retriever = rag_retriever
    
    def analyze(self, user_profile: Dict[str, Any], query: str) -> Dict[str, Any]:
        retrieved_docs = self.retriever.retrieve(query, module="investment", k=5)
        
        context = self.retriever.build_context_prompt(retrieved_docs)
        evidence = self.retriever.format_evidence(retrieved_docs)
        
        profile_summary = self._format_profile(user_profile)
        
        risk_profile = self._calculate_risk_profile(user_profile)
        allocation = self._recommend_allocation(user_profile, risk_profile)
        
        messages = [
            {"role": "system", "content": INVESTMENT_REASONING_PROMPT},
            {"role": "user", "content": f"""
User Profile:
{profile_summary}

Risk Profile: {risk_profile}
Suggested Base Allocation: {allocation}

Retrieved Investment Knowledge:
{context}

Question: {query}

Provide tax-aware investment allocation analysis with specific recommendations and citations.
"""}
        ]
        
        analysis = self.llm.generate(messages, temperature=0.3)
        
        return {
            "module": "investment_allocation",
            "analysis": analysis,
            "risk_profile": risk_profile,
            "recommended_allocation": allocation,
            "evidence": evidence,
            "tax_efficiency_score": self._calculate_tax_efficiency(allocation)
        }
    
    def _format_profile(self, profile: Dict[str, Any]) -> str:
        return f"""
- Age: {profile.get('age', 'N/A')}
- Income: ${profile.get('income', 0):,}
- Current Assets: {profile.get('assets', {})}
- Investment Goals: {profile.get('investment_goals', [])}
- Time Horizon: {profile.get('time_horizon', 'N/A')}
- Risk Tolerance: {profile.get('risk_tolerance', 'moderate')}
"""
    
    def _calculate_risk_profile(self, profile: Dict[str, Any]) -> str:
        age = profile.get('age', 40)
        risk_tolerance = profile.get('risk_tolerance', 'moderate')
        income = profile.get('income', 0)
        
        if age < 40 and risk_tolerance in ['aggressive', 'high']:
            return "Aggressive Growth"
        elif age < 50 and income > 500000:
            return "Growth with Tax Optimization"
        elif age > 60:
            return "Conservative Income-Focused"
        else:
            return "Balanced Growth and Income"
    
    def _recommend_allocation(self, profile: Dict[str, Any], risk_profile: str) -> Dict[str, float]:
        age = profile.get('age', 40)
        
        if risk_profile == "Aggressive Growth":
            return {
                "stocks": 80,
                "bonds": 10,
                "alternatives": 10,
                "cash": 0
            }
        elif risk_profile == "Growth with Tax Optimization":
            return {
                "stocks": 65,
                "municipal_bonds": 15,
                "alternatives": 15,
                "cash": 5
            }
        elif risk_profile == "Conservative Income-Focused":
            return {
                "stocks": 40,
                "bonds": 35,
                "municipal_bonds": 15,
                "cash": 10
            }
        else:
            equity_allocation = max(20, min(80, 100 - age))
            return {
                "stocks": equity_allocation,
                "bonds": 60 - equity_allocation // 2,
                "alternatives": 10,
                "cash": 30 - equity_allocation // 2
            }
    
    def _calculate_tax_efficiency(self, allocation: Dict[str, float]) -> float:
        score = 0
        score += allocation.get('municipal_bonds', 0) * 1.0
        score += allocation.get('stocks', 0) * 0.7
        score += allocation.get('alternatives', 0) * 0.5
        score += allocation.get('bonds', 0) * 0.3
        return min(100, score)

investment_module = InvestmentAllocationModule()
