from typing import Dict, Any, List
from app.agent.router import router
from app.agent.synthesizer import synthesizer
from app.modules.tax import tax_module
from app.modules.investment import investment_module
from app.modules.estate import estate_module
from app.memory.store import memory_store

class FamilyOfficeAgent:
    def __init__(self):
        self.router = router
        self.synthesizer = synthesizer
        self.memory = memory_store
        
        self.modules = {
            "tax_optimization": tax_module,
            "investment_allocation": investment_module,
            "estate_planning": estate_module
        }
    
    def process_query(self, session_id: str, question: str) -> Dict[str, Any]:
        user_profile = self.memory.get_user_profile(session_id)
        
        if not user_profile:
            return {
                "error": "No user profile found. Please complete the intake form first.",
                "requires_profile": True
            }
        
        self.memory.add_message(session_id, "user", question)
        
        routing_plan = self.router.route(question, user_profile)
        
        selected_modules = routing_plan.get("modules", [])
        
        module_results = []
        for module_name in selected_modules:
            if module_name in self.modules:
                try:
                    result = self.modules[module_name].analyze(user_profile, question)
                    module_results.append(result)
                except Exception as e:
                    print(f"Error in module {module_name}: {e}")
        
        if not module_results:
            return {
                "error": "No modules could process the query",
                "response": "I'm having trouble analyzing your question. Please try rephrasing it."
            }
        
        synthesis = self.synthesizer.synthesize(question, module_results, user_profile)
        
        self.memory.add_message(session_id, "assistant", synthesis["recommendation"])
        self.memory.add_recommendation(session_id, {
            "question": question,
            "modules_used": selected_modules,
            "breakdown": synthesis["breakdown"]
        })
        
        return {
            "response": synthesis["recommendation"],
            "breakdown": synthesis["breakdown"],
            "evidence": synthesis["evidence"],
            "modules_used": synthesis["modules_used"],
            "routing_reasoning": routing_plan.get("reasoning", "")
        }

family_office_agent = FamilyOfficeAgent()
