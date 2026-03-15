from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        
        module_results: List[Dict[str, Any]] = []
        module_names_to_run = [m for m in selected_modules if m in self.modules]
        
        if module_names_to_run:
            # Run module analyses in parallel to reduce end-to-end latency
            with ThreadPoolExecutor(max_workers=len(module_names_to_run)) as executor:
                future_to_module = {
                    executor.submit(self.modules[m].analyze, user_profile, question): m
                    for m in module_names_to_run
                }
                
                for future in as_completed(future_to_module):
                    module_name = future_to_module[future]
                    try:
                        result = future.result()
                        if isinstance(result, dict):
                            module_results.append(result)
                        else:
                            print(f"Warning: module {module_name} returned non-dict result: {type(result)}")
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
