from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid

from app.config import settings
from app.models import (
    ChatRequest, ChatResponse, ChatMessage,
    ProfileRequest, ProfileResponse, UserProfile,
    TestRequest,
)
from app.agent.orchestrator import family_office_agent
from app.memory.store import memory_store
from app.rag.vector_store import vector_store_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Family Office AI Agent...")
    try:
        vector_store_manager.initialize_stores()
        print("Vector stores initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize vector stores: {e}")
        print("RAG functionality may be limited. Please ensure corpus files exist in data/corpus/")
    
    yield
    
    print("Shutting down Family Office AI Agent...")

app = FastAPI(
    title="Family Office AI Agent",
    description="US-based Family Office planning system with tax optimization, investment allocation, and estate planning",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Family Office AI Agent",
        "version": "1.0.0",
        "status": "operational",
        "modules": ["tax_optimization", "investment_allocation", "estate_planning"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/profile/create", response_model=ProfileResponse)
async def create_profile(request: ProfileRequest):
    try:
        memory_store.create_session(request.session_id, request.profile.model_dump())
        
        return ProfileResponse(
            session_id=request.session_id,
            message="Profile created successfully",
            profile=request.profile
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/profile/update", response_model=ProfileResponse)
async def update_profile(request: ProfileRequest):
    try:
        session = memory_store.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        memory_store.update_user_profile(request.session_id, request.profile.model_dump())
        
        return ProfileResponse(
            session_id=request.session_id,
            message="Profile updated successfully",
            profile=request.profile
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/{session_id}")
async def get_profile(session_id: str):
    session = memory_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "profile": session["user_profile"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session = memory_store.get_session(request.session_id)
        
        if not session:
            if request.user_profile:
                memory_store.create_session(request.session_id, request.user_profile.model_dump())
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Session not found. Please create a profile first."
                )
        elif request.user_profile:
            memory_store.update_user_profile(request.session_id, request.user_profile.model_dump())
        
        result = family_office_agent.process_query(request.session_id, request.message)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        conversation_history = memory_store.get_conversation_history(request.session_id)
        
        return ChatResponse(
            session_id=request.session_id,
            response=result["response"],
            raw_answer=result.get("raw_answer"),
            breakdown=result["breakdown"],
            evidence=result["evidence"],
            modules_used=result["modules_used"],
            conversation_history=[
                ChatMessage(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=msg.get("timestamp")
                ) for msg in conversation_history
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/history/{session_id}")
async def get_conversation_history(session_id: str):
    session = memory_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "conversation_history": session["conversation_history"],
        "recommendations_history": session["recommendations_history"]
    }

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    memory_store.clear_session(session_id)
    return {"message": f"Session {session_id} deleted"}


# Instruction prepended for /test so the agent responds with only the letter (A/B/C/D).
TEST_MULTIPLE_CHOICE_PROMPT = (
    "This is a multiple-choice test. You must respond with ONLY the single letter of the correct answer: A, B, C, or D. "
    "Do not include any explanation, memo, or other text. Your entire response must be exactly one character: A, B, C, or D.\n\n"
)

# Minimal profile used for standardized testing (e.g. AICPA-style multiple choice).
# No client-supplied profile; each test request is independent.
TEST_DEFAULT_PROFILE = {
    "age": 40,
    "income": 100_000,
    "filing_status": "single",
    "state": "NY",
    "assets": {},
    "family": {},
    "life_events": [],
    "goals": [],
    "investment_goals": [],
    "estate_goals": [],
    "risk_tolerance": "moderate",
    "time_horizon": "long-term",
}


@app.post("/test", response_model=ChatResponse)
async def standardized_test(request: TestRequest):
    """
    Standardized testing endpoint: send a question without providing a user profile.
    Uses a fixed default profile so you can run AICPA-style or other multiple-choice
    questions. Each request is independent (new session, then discarded).
    """
    session_id = str(uuid.uuid4())
    try:
        memory_store.create_session(session_id, TEST_DEFAULT_PROFILE)
        test_message = TEST_MULTIPLE_CHOICE_PROMPT + request.message.strip()
        result = family_office_agent.process_query(session_id, test_message)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        history = memory_store.get_conversation_history(session_id)
        return ChatResponse(
            session_id=session_id,
            response=result["response"],
            raw_answer=result.get("raw_answer"),
            breakdown=result["breakdown"],
            evidence=result["evidence"],
            modules_used=result["modules_used"],
            conversation_history=[
                ChatMessage(role=msg["role"], content=msg["content"], timestamp=msg.get("timestamp"))
                for msg in history
            ],
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Test endpoint error: {type(e).__name__}: {str(e)}")
    finally:
        memory_store.clear_session(session_id)


@app.post("/session/new")
async def create_new_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
