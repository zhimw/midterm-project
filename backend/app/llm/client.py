import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from groq import Groq
from app.config import settings
from google import genai
from google.genai import types

class LLMClient:
    def __init__(self, provider: str = None):
        self.provider = provider or settings.llm_provider
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = "gpt-4o-mini"
        elif self.provider == "gemini":
            # New Google GenAI SDK client (google-genai)
            self.client = genai.Client(api_key=settings.gemini_api_key)
            # Use a current Gemini model from the new SDK
            self.model = "gemini-2.5-flash"
        elif self.provider == "groq":
            self.client = Groq(api_key=settings.groq_api_key)
            self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
        disable_thinking: bool = False,
    ) -> str:
        if self.provider == "openai":
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        
        elif self.provider == "gemini":
            # Flatten OpenAI-style messages into a single text prompt for Gemini
            # using the new google-genai SDK.
            prompt_lines = []
            for msg in messages:
                role = msg.get("role", "user")
                if role == "system":
                    prefix = "System"
                elif role == "assistant":
                    prefix = "Assistant"
                else:
                    prefix = "User"
                prompt_lines.append(f"{prefix}: {msg.get('content', '')}")

            prompt_text = "\n".join(prompt_lines)

            # Configure generation; when json_mode is requested, ask Gemini
            # to return proper JSON instead of free-form text.
            gen_config_kwargs: Dict[str, Any] = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if json_mode:
                # Hint to the model that the response must be strict JSON.
                # This is supported by the new google-genai SDK.
                gen_config_kwargs["response_mime_type"] = "application/json"
            if disable_thinking:
                # Gemini 2.5 Flash is a thinking model. By default it spends a large
                # hidden token budget on internal reasoning before producing output.
                # For short deterministic tasks (routing, MC answers) this means the
                # visible output can be empty or truncated. Setting thinking_budget=0
                # disables that reasoning phase so all tokens go to the actual reply.
                gen_config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

            response = self.client.models.generate_content(
                model=self.model,
                contents=types.Part.from_text(text=prompt_text),
                config=types.GenerateContentConfig(**gen_config_kwargs),
            )
            # response.text can be None when blocked or empty; return "" as a safe fallback.
            return response.text or ""
        
        elif self.provider == "groq":
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

llm_client = LLMClient()
