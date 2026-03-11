# Family Office AI Agent

An intelligent Family Office planning system that provides comprehensive financial guidance across tax optimization, investment allocation, and estate planning for high-net-worth US families.

## Overview

This AI agent combines multi-step reasoning, RAG (Retrieval-Augmented Generation), and domain expertise to deliver personalized, explainable recommendations for complex family office scenarios.

### Key Capabilities

**Tax Optimization (Core Engine)**
- Federal and state tax analysis
- Tax-loss harvesting strategies
- Entity structuring recommendations
- Qualified Opportunity Zones
- 1031 exchanges and charitable giving
- Retirement account optimization

**Investment Allocation (Tax-Aware)**
- Risk-adjusted portfolio recommendations
- Asset location optimization
- Municipal bonds vs taxable bonds analysis
- Direct indexing and tax-loss harvesting
- Qualified dividends strategies
- Alternative investments guidance

**Estate & Trust Planning (Life-Event Driven)**
- Trust structure recommendations
- Generation-skipping transfer strategies
- Annual gifting optimization
- Life insurance planning
- Business succession planning
- Guardianship provisions

## Architecture

```
User Profile Input (age, income, assets, family, goals)
           ↓
    Router Agent (LLM-based intent classification)
           ↓
┌──────────┬────────────────┬───────────────┐
│   Tax    │  Investment    │    Estate     │
│  Module  │    Module      │    Module     │
│  (RAG)   │     (RAG)      │     (RAG)     │
└──────────┴────────────────┴───────────────┘
           ↓
  Synthesizer (Integrated recommendations)
           ↓
    Final Advice + Breakdown + Evidence
           ↓
  Risk & Ethics Disclaimer
```

## Technology Stack

**Backend**
- Python 3.10+
- FastAPI (async web framework)
- LangChain (RAG orchestration)
- FAISS (vector similarity search)
- Sentence Transformers (embeddings)
- OpenAI / Gemini / Groq (LLM providers)

**Frontend**
- React 18
- TypeScript
- Vite (build tool)
- Recharts (data visualization)
- Axios (API client)

## Features

### 1. Intelligent Routing
- LLM-based intent classification
- Multi-module coordination
- Context-aware query understanding

### 2. Domain-Specific RAG
- Separate knowledge bases for Tax, Investment, Estate
- Semantic search with citation tracking
- Evidence-based recommendations

### 3. Memory System
- Session-based conversation history
- Profile persistence across interactions
- Recommendations tracking

### 4. Explainable AI
- Cited sources for all recommendations
- Visual breakdowns of analysis
- Transparent reasoning chains

### 5. Professional Disclaimers
- Clear educational purpose statements
- Guidance to consult professionals
- Risk and compliance awareness

## Quick Start

See [QUICKSTART.md](./QUICKSTART.md) for detailed setup instructions.

```bash
# 1. Setup backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload

# 2. Setup frontend (in new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev

# 3. Open browser
# http://localhost:5173
```

## Project Structure

```
midterm-project/
├── backend/
│   ├── app/
│   │   ├── llm/              # LLM client (OpenAI/Gemini/Groq)
│   │   ├── rag/              # RAG system (FAISS + embeddings)
│   │   ├── modules/          # Domain modules (Tax/Investment/Estate)
│   │   ├── agent/            # Agent orchestration (Router/Synthesizer)
│   │   ├── memory/           # Conversation memory
│   │   ├── models.py         # Pydantic models
│   │   ├── config.py         # Configuration
│   │   └── main.py           # FastAPI application
│   ├── data/corpus/          # Knowledge bases (JSONL)
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── types/            # TypeScript types
│   │   ├── utils/            # API client
│   │   ├── App.tsx           # Main application
│   │   └── main.tsx          # Entry point
│   ├── package.json
│   └── README.md
├── README.md                 # This file
└── QUICKSTART.md             # Setup guide
```

## Knowledge Base

The system includes curated financial planning knowledge:

- **Tax Knowledge** (12 documents): Federal/state taxes, capital gains, deductions, entity structures
- **Investment Knowledge** (12 documents): Asset allocation, tax efficiency, municipal bonds, risk management
- **Estate Knowledge** (12 documents): Trusts, gifting, generation-skipping, business succession

Knowledge bases are in JSONL format with unique `doc_id` for citation tracking.

## AI Techniques

### Multi-Step Reasoning
- Router analyzes intent and selects appropriate modules
- Each module performs specialized analysis
- Synthesizer integrates insights into cohesive recommendations

### RAG (Retrieval-Augmented Generation)
- Vector similarity search using sentence-transformers
- Top-k retrieval with configurable k
- Citation-based grounding to prevent hallucination

### Memory
- Short-term: Conversation history (in-memory)
- Long-term: User profile persistence
- Contextual awareness across interactions

### Rule-Based + LLM Hybrid
- Rule-based calculations (estate value, allocation, triggers)
- LLM reasoning for complex scenarios and explanations
- Combined for reliability and flexibility

## Example Queries

**Tax Optimization**
- "What tax strategies should I consider given my $850K income?"
- "How can I minimize capital gains tax on my stock portfolio?"
- "Should I consider a 1031 exchange for my rental property?"

**Investment Allocation**
- "What's an optimal asset allocation for my risk profile?"
- "How should I balance municipal bonds vs taxable bonds?"
- "What are tax-efficient investment strategies for high earners?"

**Estate Planning**
- "Do I need estate planning with $5M in assets?"
- "What trust structures should I consider for my children?"
- "How can I minimize estate taxes for my family?"

**Integrated**
- "I'm 45 with $850K income and 2 kids. What should I prioritize?"
- "I just sold my business for $10M. What are my next steps?"
- "How do I coordinate tax, investment, and estate strategies?"

## Limitations & Disclaimers

This system is designed for **educational and informational purposes only**. It does NOT provide:
- Personalized financial advice
- Tax advice
- Legal advice
- Investment recommendations

Users must consult qualified professionals:
- Certified Public Accountants (CPAs)
- Tax attorneys
- Registered Investment Advisors (RIAs)
- Estate planning attorneys

## Security & Privacy

- No data persistence (sessions stored in-memory only)
- No user authentication (not production-ready)
- API keys stored in `.env` (never commit)
- CORS protection enabled
- For production: Add authentication, encryption, database, audit logs

## Contributing

This is an educational project for EECS6895.

To extend the system:
1. Add knowledge to corpus files (`backend/data/corpus/*.jsonl`)
2. Enhance modules in `backend/app/modules/`
3. Improve prompts in `backend/app/llm/prompts.py`
4. Add visualizations to frontend components

## License

Educational use only. Not for production financial advice.

## Support

For issues or questions about setup, see:
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [QUICKSTART.md](./QUICKSTART.md)
