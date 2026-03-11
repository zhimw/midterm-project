from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class ConversationMemory:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str, user_profile: Dict[str, Any]) -> None:
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_profile": user_profile,
            "conversation_history": [],
            "recommendations_history": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        self.sessions[session_id]["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    def add_recommendation(self, session_id: str, recommendation: Dict[str, Any]) -> None:
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        recommendation["timestamp"] = datetime.now().isoformat()
        self.sessions[session_id]["recommendations_history"].append(recommendation)
        self.sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    def get_conversation_history(self, session_id: str, limit: int = None) -> List[Dict[str, str]]:
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id]["conversation_history"]
        if limit:
            return history[-limit:]
        return history
    
    def get_user_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        return session["user_profile"] if session else None
    
    def update_user_profile(self, session_id: str, updates: Dict[str, Any]) -> None:
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        self.sessions[session_id]["user_profile"].update(updates)
        self.sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    def get_recommendations_history(self, session_id: str) -> List[Dict[str, Any]]:
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id]["recommendations_history"]
    
    def clear_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]

memory_store = ConversationMemory()
