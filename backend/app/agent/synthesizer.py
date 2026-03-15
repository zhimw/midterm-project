from typing import Dict, Any, List
import re
import json
from app.llm.client import llm_client
from app.llm.prompts import SYNTHESIZER_SYSTEM_PROMPT, RISK_DISCLAIMER

# When the question starts with this (from /test endpoint), respond with only A, B, C, or D.
MULTIPLE_CHOICE_PREFIX = "This is a multiple-choice test."


class RecommendationSynthesizer:
    def __init__(self):
        self.llm = llm_client

    def _is_multiple_choice(self, question: str) -> bool:
        return question.strip().startswith(MULTIPLE_CHOICE_PREFIX)

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
        multiple_choice = self._is_multiple_choice(question)

        raw_answer: str | None = None

        if multiple_choice:
            # Strip the test prefix so the model sees the clean question + answer choices.
            clean_question = question[len(MULTIPLE_CHOICE_PREFIX):].strip()
            system = "You are a tax/finance expert. Answer multiple-choice questions with ONLY the single letter of the correct answer: A, B, C, or D. No explanation, no other text."
            user_content = f"""Question:
{clean_question}

Module Analyses:
{combined_context}

Based on the question and the analyses above, reply with ONLY the single letter of the correct answer: A, B, C, or D."""
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content}
            ]
            raw_answer = self.llm.generate(messages, temperature=0, max_tokens=256, disable_thinking=True)
            # Normalize to a single letter for scoring; guard against None or empty,
            # using logic similar to run_standardized_tests.normalize_answer.
            text = (raw_answer or "").strip().upper()
            if not text:
                final_recommendation = "?"
            else:
                letter_match = re.search(r"\b([A-D])\b", text)
                if letter_match:
                    final_recommendation = letter_match.group(1)
                else:
                    # Fallback: take first character, uppercased
                    final_recommendation = text[:1]
            # No disclaimer in test mode
        else:
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
            raw_answer = final_recommendation

        breakdown = self._create_breakdown(module_results)
        
        return {
            "recommendation": final_recommendation,
            "raw_answer": raw_answer,
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
