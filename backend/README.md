# Family Office AI Agent - Backend

Python FastAPI backend for the Family Office AI planning system.

## Architecture

```
User Query → Router → Domain Modules (Tax/Investment/Estate) → RAG Retrieval → LLM Reasoning → Synthesizer → Response
                              ↓
                         Memory Store (Session Management)
```

## Core Components

### 1. LLM Client (`app/llm/client.py`)
- Uses **Google Gemini** for all LLM calls
- Configurable via environment variables

### 2. RAG System (`app/rag/`)
- Vector store management with FAISS
- Sentence-transformers embeddings
- Module-specific knowledge bases (tax, investment, estate)

### 3. Domain Modules (`app/modules/`)
- **Tax Optimization**: Tax strategies, deductions, entity structuring
- **Investment Allocation**: Tax-aware portfolio recommendations
- **Estate Planning**: Trust structures, wealth transfer strategies

### 4. Agent System (`app/agent/`)
- **Router**: Intent classification for module selection
- **Orchestrator**: Executes multi-module workflows
- **Synthesizer**: Integrates insights into cohesive recommendations

### 5. Memory System (`app/memory/`)
- Session-based conversation history
- User profile persistence
- Recommendations tracking

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
```

### 3. Verify Corpus Files

Ensure knowledge base files exist:
```
data/corpus/
├── tax_knowledge.jsonl
├── investment_knowledge.jsonl
└── estate_knowledge.jsonl
```

## Running the Server

### Development Mode
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Production Mode
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Session Management
- `POST /session/new` - Create new session ID
- `DELETE /session/{session_id}` - Delete session

### Profile Management
- `POST /profile/create` - Create user profile
- `POST /profile/update` - Update user profile
- `GET /profile/{session_id}` - Retrieve user profile

### Chat Interface
- `POST /chat` - Send message and receive AI recommendation
  - Request: `{ "session_id": "...", "message": "...", "user_profile": {...} }`
  - Response: `{ "response": "...", "breakdown": {...}, "evidence": [...], "modules_used": [...] }`

### History
- `GET /history/{session_id}` - Get conversation and recommendation history

### Health
- `GET /` - Service info
- `GET /health` - Health check

## API Usage Example

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Create session
response = requests.post(f"{BASE_URL}/session/new")
session_id = response.json()["session_id"]

# 2. Create profile
profile = {
    "session_id": session_id,
    "profile": {
        "age": 45,
        "income": 850000,
        "filing_status": "married",
        "state": "NY",
        "assets": {
            "cash": 200000,
            "stocks": 2500000,
            "bonds": 500000,
            "real_estate": 1800000
        },
        "family": {
            "marital_status": "married",
            "children": 2
        },
        "risk_tolerance": "moderate",
        "goals": ["retirement planning", "college funding", "estate planning"]
    }
}
requests.post(f"{BASE_URL}/profile/create", json=profile)

# 3. Ask question
chat_request = {
    "session_id": session_id,
    "message": "What tax strategies should I consider given my income level?"
}
response = requests.post(f"{BASE_URL}/chat", json=chat_request)
print(response.json()["response"])
```

## Knowledge Base Format

Each JSONL file contains domain knowledge in the format:
```json
{"doc_id": "tax_001", "category": "federal_income", "text": "Content..."}
```

To add knowledge:
1. Add entries to appropriate `data/corpus/*.jsonl` file
2. Restart server to rebuild vector stores
3. Each doc_id must be unique for citation tracking

## LLM Provider Configuration

### Gemini
- Model: `gemini-2.5-flash`
- Notes: This project is configured to use Gemini only.

## Troubleshooting

### Vector Store Initialization Fails
- Verify corpus files exist in `data/corpus/`
- Check file format is valid JSONL
- Ensure `sentence-transformers` is installed

### LLM API Errors
- Verify API keys are set in `.env`
- Check API rate limits and quotas
- Ensure `LLM_PROVIDER` matches configured key

### Memory/Session Issues
- Sessions are in-memory only (restart clears all)
- For persistent storage, integrate Redis or database

## Technology Stack

- **FastAPI** - Modern async web framework
- **LangChain** - RAG and document processing
- **FAISS** - Vector similarity search
- **Sentence Transformers** - Text embeddings
- **Pydantic** - Data validation and serialization
