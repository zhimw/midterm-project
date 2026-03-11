from typing import Dict, Any, List
from app.llm.client import llm_client
from app.llm.prompts import TAX_REASONING_PROMPT
from app.rag.retriever import rag_retriever

class TaxOptimizationModule:
    def __init__(self):
        self.llm = llm_client
        self.retriever = rag_retriever
    
    def analyze(self, user_profile: Dict[str, Any], query: str) -> Dict[str, Any]:
        retrieved_docs = self.retriever.retrieve(query, module="tax", k=5)
        
        context = self.retriever.build_context_prompt(retrieved_docs)
        evidence = self.retriever.format_evidence(retrieved_docs)
        
        profile_summary = self._format_profile(user_profile)
        
        messages = [
            {"role": "system", "content": TAX_REASONING_PROMPT},
            {"role": "user", "content": f"""
User Profile:
{profile_summary}

Retrieved Tax Knowledge:
{context}

Question: {query}

Provide tax optimization analysis with specific strategies and citations.
"""}
        ]
        
        analysis = self.llm.generate(messages, temperature=0.3)
        
        strategies = self._extract_strategies(analysis)
        
        return {
            "module": "tax_optimization",
            "analysis": analysis,
            "strategies": strategies,
            "evidence": evidence,
            "key_considerations": self._extract_key_considerations(user_profile)
        }
    
    def _format_profile(self, profile: Dict[str, Any]) -> str:
        return f"""
- Income: ${profile.get('income', 0):,}
- Age: {profile.get('age', 'N/A')}
- Filing Status: {profile.get('filing_status', 'N/A')}
- State: {profile.get('state', 'N/A')}
- Asset Allocation: {profile.get('assets', {})}
- Life Events: {profile.get('life_events', [])}
"""
    
    def _extract_strategies(self, analysis: str) -> List[str]:
        strategies = []
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                strategies.append(line.lstrip('-•* '))
        return strategies[:5]
    
    def _extract_key_considerations(self, profile: Dict[str, Any]) -> List[str]:
        considerations = []
        
        income = profile.get('income', 0)
        if income > 1000000:
            considerations.append("High income subject to Net Investment Income Tax (3.8%)")
        if income > 578125:
            considerations.append("Top federal marginal rate (37%)")
        
        assets = profile.get('assets', {})
        if assets.get('real_estate', 0) > 500000:
            considerations.append("Consider 1031 exchange for real estate transactions")
        
        if assets.get('stocks', 0) > 1000000:
            considerations.append("Tax-loss harvesting opportunities in equity portfolio")
        
        return considerations

tax_module = TaxOptimizationModule()
