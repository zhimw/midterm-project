from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class UserProfile(BaseModel):
    age: int = Field(..., description="User's age")
    income: float = Field(..., description="Annual income")
    filing_status: str = Field(default="single", description="Tax filing status")
    state: str = Field(default="NY", description="State of residence")
    assets: Dict[str, float] = Field(default_factory=dict, description="Asset breakdown")
    family: Dict[str, Any] = Field(default_factory=dict, description="Family structure")
    life_events: List[str] = Field(default_factory=list, description="Recent life events")
    goals: List[str] = Field(default_factory=list, description="Financial goals")
    investment_goals: List[str] = Field(default_factory=list, description="Investment objectives")
    estate_goals: List[str] = Field(default_factory=list, description="Estate planning goals")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance level")
    time_horizon: str = Field(default="long-term", description="Investment time horizon")

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str
    user_profile: Optional[UserProfile] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    raw_answer: Optional[str] = Field(default=None, description="Full agent answer before any normalization (for MC tests)")
    breakdown: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    modules_used: List[str]
    conversation_history: List[ChatMessage]

class TestRequest(BaseModel):
    """Request for standardized testing: no user profile required."""
    message: str = Field(..., description="Question or prompt to send to the agent")

class DirectTestResponse(BaseModel):
    """Response from the direct (no-RAG, no-agent) test endpoint."""
    response: str = Field(..., description="Normalized letter answer (A/B/C/D)")
    raw_answer: str = Field(..., description="Full model output before normalization")

class ScenarioTestRequest(BaseModel):
    """Request for scenario-based open-ended testing with a custom user profile."""
    profile: UserProfile
    question: str = Field(..., description="Open-ended planning question to ask the agent")

class ScenarioTestResponse(BaseModel):
    """Response from the scenario test endpoint."""
    response: str = Field(..., description="Agent's full recommendation")
    breakdown: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    modules_used: List[str]

class JudgeRequest(BaseModel):
    """Request to the LLM judge endpoint."""
    response: str = Field(..., description="The agent response to evaluate")
    rubric: str = Field(..., description="Grading rubric describing what a good answer must cover")
    max_response_chars: int = Field(default=3000, description="Truncate response to this many chars before judging")

class JudgeResponse(BaseModel):
    """Result from the LLM judge endpoint."""
    score: Optional[int] = Field(..., description="Score 1-10, or null on failure")
    justification: Optional[str] = Field(..., description="One-sentence reason for the score")
    provider: str = Field(..., description="LLM provider used for judging")

class ProfileRequest(BaseModel):
    session_id: str
    profile: UserProfile

class ProfileResponse(BaseModel):
    session_id: str
    message: str
    profile: UserProfile
