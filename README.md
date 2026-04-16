# Family Office AI Agent

An intelligent multi-agent planning system for high-net-worth US families, providing integrated financial guidance across **tax optimization**, **investment allocation**, and **estate planning** through a RAG-augmented architecture powered by **Google Gemini**.

> **Course Project** — Columbia University EECS6895 (Big Data Analytics)  
> **Demo Video**: [Google Drive Link — add your link here]  
> **GitHub**: [https://github.com/YOUR_GITHUB/midterm-project](https://github.com/YOUR_GITHUB/midterm-project)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the System](#running-the-system)
- [Example Usage](#example-usage)
- [Project Structure](#project-structure)
- [Evaluation](#evaluation)
- [Limitations](#limitations)

---

## Overview

The Family Office AI Agent combines **multi-agent orchestration**, **Retrieval-Augmented Generation (RAG)**, and **domain-specific reasoning** to answer complex financial planning questions. Users complete a brief intake form (age, income, assets, family structure, goals) and then ask natural-language questions. The system:

1. Classifies the query with an LLM-based **router** (tax / investment / estate)
2. Retrieves supporting evidence via **FAISS semantic search** across three curated knowledge bases
3. Runs **domain-specific modules in parallel** (ThreadPoolExecutor)
4. **Synthesizes** a cited, integrated recommendation with source tracking
5. Appends a **professional risk disclaimer** for all advice

### Key Capabilities

| Domain | Capabilities |
|--------|-------------|
| **Tax Optimization** | Federal/state analysis, capital gains, tax-loss harvesting, 1031 exchanges, QOZs, charitable giving, entity structuring, retirement accounts |
| **Investment Allocation** | Risk-adjusted portfolios, asset location, municipal bonds, direct indexing, tax efficiency scoring |
| **Estate Planning** | Trust structures (ILIT, SLAT, QPRT, Dynasty), GST, annual gifting, life insurance, business succession |

---

## Architecture

```
┌─────────────────────────────────────┐
│         User Intake Form            │
│  (age, income, assets, goals, risk) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Router Agent (LLM-based)       │
│   Classifies query → module(s)      │
└────┬─────────────┬──────────────────┘
     │             │             │
     ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐
│  Tax   │  │Investment│  │ Estate   │
│ Module │  │  Module  │  │  Module  │
│ (RAG)  │  │  (RAG)   │  │  (RAG)   │
└────┬───┘  └────┬─────┘  └────┬─────┘
     │           │              │
     └───────────┴──────────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │ Synthesizer (LLM)     │
     │ Integrated response + │
     │ citations + breakdown │
     └───────────┬───────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │ Risk Disclaimer       │
     │ + Evidence Panel      │
     └───────────────────────┘
```

### Knowledge Base

| Domain | Documents | Sources |
|--------|-----------|---------|
| Tax | 838 | IRS Publications p17, p523, p526, p550, p590a, p590b |
| Investment | 168 | Fidelity & Vanguard capital market assumption reports |
| Estate | 112 | Curated estate planning references |

Embeddings: `sentence-transformers/all-MiniLM-L6-v2` · Vector DB: FAISS · Top-k: 5

---

## Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.10+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| LLM API Key | — | Google Gemini |

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_GITHUB/midterm-project.git
cd midterm-project
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `backend/.env` and set your LLM provider:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

### 4. Frontend Setup

```bash
# In a new terminal, from the project root
cd frontend
npm install
cp .env.example .env
```

The default `frontend/.env` already points to `http://localhost:8000` — no changes needed for local development.

---

## Running the System

### Start the Backend

```bash
cd backend
source venv/bin/activate        # if using virtualenv
uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Initializing Family Office AI Agent...
INFO:     Vector stores initialized successfully
```

> **Note:** On first run, FAISS indices are built from the JSONL corpus files (takes ~30–60 seconds). Subsequent starts load cached indices instantly.

### Start the Frontend

```bash
# In a separate terminal
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Example Usage

### Via the Web UI

1. Open [http://localhost:5173](http://localhost:5173)
2. Complete the **4-step intake form**:
   - Step 1: Age, income, filing status, state
   - Step 2: Assets (cash, stocks, bonds, real estate)
   - Step 3: Family & life events
   - Step 4: Goals & risk tolerance
3. Ask questions in the chat interface, for example:
   - *"What tax strategies should I prioritize given my $850K income and 2 kids?"*
   - *"How should I allocate my portfolio to minimize taxes?"*
   - *"Do I need estate planning with $5M in assets?"*

### Via the REST API

**Create a session and profile:**
```bash
SESSION=$(curl -s -X POST http://localhost:8000/session/new | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
```
```bash
curl -s -X POST http://localhost:8000/profile/create \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION\",
    \"profile\": {
      \"age\": 45,
      \"income\": 850000,
      \"filing_status\": \"married_filing_jointly\",
      \"state\": \"CA\",
      \"assets\": {\"stocks\": 2000000, \"real_estate\": 1500000, \"cash\": 300000},
      \"family\": {\"children\": 2, \"marital_status\": \"married\"},
      \"risk_tolerance\": \"moderate\",
      \"time_horizon\": \"long_term\"
    }
  }"
```

**Send a chat message:**
```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION\",
    \"message\": \"What are the most important tax strategies for someone in my situation?\"
  }" | python3 -m json.tool
```

**Response structure** (see `ChatResponse` in `backend/app/models.py`; keys vary by query):

```json
{
  "session_id": "uuid-here",
  "response": "Based on your profile...",
  "raw_answer": null,
  "breakdown": { "tax_strategies": [], "investment_allocation": {}, "estate_triggers": [] },
  "evidence": [{ "doc_id": "tax_001", "category": "federal_tax", "snippet": "..." }],
  "modules_used": ["tax_optimization", "investment_allocation"],
  "conversation_history": []
}
```

### Via the CLI Script

```bash
cd backend
source venv/bin/activate

# Interactive (omit arguments; empty line to quit)
python3 scripts/query_agent.py

# One-shot query (positional message)
python3 scripts/query_agent.py "How can I minimize capital gains taxes?"
```

### Run Evaluation Benchmarks

```bash
cd backend
source venv/bin/activate

# Multiple-choice benchmark (78 AICPA-style questions)
python3 scripts/run_standardized_tests.py

# RAG+Agent vs Direct LLM comparison
python3 scripts/compare_tests.py

# Open-ended scenario evaluation (15 scenarios with LLM-as-judge)
python3 scripts/run_scenario_tests.py
```

---

## Project Structure

```
midterm-project/
├── README.md
├── QUICKSTART.md
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + all API routes
│   │   ├── models.py            # Pydantic request/response models
│   │   ├── config.py            # Settings (LLM provider, CORS, RAG params)
│   │   ├── agent/
│   │   │   ├── orchestrator.py  # FamilyOfficeAgent — top-level query processor
│   │   │   ├── router.py        # LLM-based intent/module classifier
│   │   │   └── synthesizer.py   # Integrates module outputs into final response
│   │   ├── llm/
│   │   │   ├── client.py        # LLM client (Google Gemini)
│   │   │   └── prompts.py       # System prompts + risk disclaimer
│   │   ├── modules/
│   │   │   ├── tax.py           # Tax optimization module
│   │   │   ├── investment.py    # Investment allocation module
│   │   │   └── estate.py        # Estate planning module
│   │   ├── rag/
│   │   │   ├── retriever.py     # RAG retriever wrapper
│   │   │   └── vector_store.py  # FAISS vector store manager
│   │   └── memory/
│   │       └── store.py         # In-memory session/conversation storage
│   ├── data/
│   │   ├── corpus/              # JSONL knowledge bases (tax/investment/estate)
│   │   └── faiss_index/         # Cached FAISS vector indices
│   ├── scripts/
│   │   ├── query_agent.py       # CLI query tool
│   │   ├── run_standardized_tests.py  # AICPA benchmark runner
│   │   ├── run_scenario_tests.py      # Open-ended scenario evaluator
│   │   └── compare_tests.py           # Agent vs baseline comparison
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Root component (session + state management)
│   │   ├── components/
│   │   │   ├── IntakeForm.tsx   # 4-step user profile wizard
│   │   │   ├── ChatInterface.tsx# Conversation display + input
│   │   │   ├── BreakdownPanel.tsx  # Module output visualization
│   │   │   └── EvidencePanel.tsx   # RAG source citations
│   │   ├── types/index.ts       # TypeScript interfaces
│   │   └── utils/api.ts         # Axios API client
│   ├── package.json
│   └── .env.example
│
└── raw/                         # Source PDFs for knowledge base construction
    ├── tax/                     # IRS publications
    └── investment/              # Capital market assumption reports
```

---

## Evaluation

The system was evaluated using two complementary tracks:

### Track 1 — AICPA Multiple-Choice Benchmark (78 questions)

| System | Accuracy |
|--------|----------|
| RAG + Agent | **87.2%** (68/78) |
| Direct LLM (baseline) | 83.3% (65/78) |

### Track 2 — Open-Ended Scenario Quality (15 scenarios)

| Metric | Score |
|--------|-------|
| Average keyword coverage | **67.7%** |
| Average LLM-as-judge score | **7.4 / 10** |

Scenarios cover tech executives, business owners, young professionals, retirees, and high-estate-value clients.

---

## Technology Stack

**Backend:** Python 3.10 · FastAPI · LangChain · FAISS · Sentence Transformers · Google Gemini

**Frontend:** React 18 · TypeScript · Vite · Recharts · Axios

---

## Limitations

- **No authentication** — sessions are in-memory only; not production-ready
- **Knowledge cutoff** — corpus reflects 2024 tax year data (IRS publications + capital market reports as of build date)
- **Educational only** — not a substitute for licensed financial, tax, or legal advice
- **No persistence** — session data is lost on server restart

---

## License

Educational use only. Not for production financial advice.  
For setup help see [QUICKSTART.md](./QUICKSTART.md).
