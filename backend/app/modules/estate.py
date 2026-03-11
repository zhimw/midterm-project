from typing import Dict, Any, List
from app.llm.client import llm_client
from app.llm.prompts import ESTATE_REASONING_PROMPT
from app.rag.retriever import rag_retriever

class EstatePlanningModule:
    def __init__(self):
        self.llm = llm_client
        self.retriever = rag_retriever
    
    def analyze(self, user_profile: Dict[str, Any], query: str) -> Dict[str, Any]:
        retrieved_docs = self.retriever.retrieve(query, module="estate", k=5)
        
        context = self.retriever.build_context_prompt(retrieved_docs)
        evidence = self.retriever.format_evidence(retrieved_docs)
        
        profile_summary = self._format_profile(user_profile)
        
        estate_value = self._calculate_estate_value(user_profile)
        triggers = self._identify_planning_triggers(user_profile)
        
        messages = [
            {"role": "system", "content": ESTATE_REASONING_PROMPT},
            {"role": "user", "content": f"""
User Profile:
{profile_summary}

Estimated Estate Value: ${estate_value:,}
Planning Triggers: {triggers}

Retrieved Estate Planning Knowledge:
{context}

Question: {query}

Provide estate planning analysis with specific strategies and citations.
"""}
        ]
        
        analysis = self.llm.generate(messages, temperature=0.3)
        
        return {
            "module": "estate_planning",
            "analysis": analysis,
            "estate_value": estate_value,
            "planning_triggers": triggers,
            "evidence": evidence,
            "recommended_structures": self._recommend_structures(user_profile, estate_value)
        }
    
    def _format_profile(self, profile: Dict[str, Any]) -> str:
        family = profile.get('family', {})
        return f"""
- Age: {profile.get('age', 'N/A')}
- Marital Status: {family.get('marital_status', 'N/A')}
- Children: {family.get('children', 0)}
- Total Assets: {profile.get('assets', {})}
- Life Events: {profile.get('life_events', [])}
- Estate Goals: {profile.get('estate_goals', [])}
"""
    
    def _calculate_estate_value(self, profile: Dict[str, Any]) -> float:
        assets = profile.get('assets', {})
        total = sum([
            assets.get('cash', 0),
            assets.get('stocks', 0),
            assets.get('bonds', 0),
            assets.get('real_estate', 0),
            assets.get('business', 0),
            assets.get('other', 0)
        ])
        return total
    
    def _identify_planning_triggers(self, profile: Dict[str, Any]) -> List[str]:
        triggers = []
        
        estate_value = self._calculate_estate_value(profile)
        if estate_value > 13610000:
            triggers.append("Estate value exceeds federal exemption - estate tax planning needed")
        
        life_events = profile.get('life_events', [])
        if 'marriage' in life_events:
            triggers.append("Recent marriage - update beneficiaries and estate documents")
        if 'birth' in life_events or 'adoption' in life_events:
            triggers.append("New child - establish trusts and guardianship provisions")
        if 'divorce' in life_events:
            triggers.append("Divorce - immediate estate plan revision required")
        if 'business_sale' in life_events:
            triggers.append("Business liquidity event - sophisticated wealth transfer strategies")
        
        family = profile.get('family', {})
        if family.get('children', 0) > 0:
            triggers.append("Minor children - consider education trusts and UTMA/UGMA accounts")
        
        age = profile.get('age', 0)
        if age > 65:
            triggers.append("Retirement age - review beneficiary designations and RMD strategies")
        
        return triggers
    
    def _recommend_structures(self, profile: Dict[str, Any], estate_value: float) -> List[Dict[str, str]]:
        structures = []
        
        if estate_value > 13610000:
            structures.append({
                "type": "Irrevocable Life Insurance Trust (ILIT)",
                "purpose": "Remove life insurance proceeds from taxable estate"
            })
            structures.append({
                "type": "Spousal Lifetime Access Trust (SLAT)",
                "purpose": "Transfer wealth while maintaining indirect access"
            })
        
        family = profile.get('family', {})
        if family.get('children', 0) > 0:
            structures.append({
                "type": "529 Education Savings Plan",
                "purpose": "Tax-free growth for education expenses"
            })
            if estate_value > 5000000:
                structures.append({
                    "type": "Dynasty Trust",
                    "purpose": "Multi-generational wealth transfer, GST tax optimization"
                })
        
        if profile.get('assets', {}).get('real_estate', 0) > 2000000:
            structures.append({
                "type": "Qualified Personal Residence Trust (QPRT)",
                "purpose": "Transfer home at discounted value for estate tax purposes"
            })
        
        return structures

estate_module = EstatePlanningModule()
