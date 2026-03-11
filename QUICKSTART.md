# Family Office AI Agent - Quick Start Guide

Get the Family Office AI Agent running on your local machine in 10 minutes.

## Prerequisites

- **Python 3.10+** (check: `python3 --version`)
- **Node.js 18+** (check: `node --version`)
- **npm or yarn** (check: `npm --version`)
- **API Key** for at least one LLM provider:
  - OpenAI API key (recommended), OR
  - Google Gemini API key, OR
  - Groq API key

## Step-by-Step Setup

### Step 1: Clone/Navigate to Project

```bash
cd midterm-project
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create Python virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

**Edit `backend/.env` with your API key:**

For OpenAI (recommended):
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

For Gemini:
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
```

For Groq:
```
LLM_PROVIDER=groq
GROQ_API_KEY=your-key-here
```

### Step 3: Start Backend Server

```bash
# Still in backend/ directory
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Initializing Family Office AI Agent...
INFO:     Vector stores initialized successfully
```

**Keep this terminal running.**

### Step 4: Frontend Setup

Open a **new terminal** window:

```bash
# Navigate to frontend
cd midterm-project/frontend

# Install dependencies
npm install

# Configure environment (optional)
cp .env.example .env
```

### Step 5: Start Frontend

```bash
# Still in frontend/ directory
npm run dev
```

You should see:
```
  VITE v5.0.11  ready in 500 ms

  ➜  Local:   http://localhost:5173/
```

### Step 6: Open Browser

Navigate to: **http://localhost:5173**

## Usage Guide

### 1. Complete Intake Form

Fill out the 4-step intake form:

**Step 1: Basic Information**
- Age: 45
- Income: $850,000
- Filing Status: Married Filing Jointly
- State: New York

**Step 2: Assets**
- Cash: $200,000
- Stocks: $2,500,000
- Bonds: $500,000
- Real Estate: $1,800,000

**Step 3: Family & Life Events**
- Marital Status: Married
- Children: 2
- Life Events: Select any applicable

**Step 4: Goals & Risk**
- Financial Goals: Select your priorities
- Investment Goals: Check "tax efficiency"
- Risk Tolerance: Moderate
- Time Horizon: Long-term (10+ years)

Click **Start Planning** to begin.

### 2. Ask Questions

Try these example queries:

**Tax-Focused:**
```
What tax strategies should I consider given my income level?
```

**Investment-Focused:**
```
What's an optimal asset allocation for my risk profile?
```

**Estate-Focused:**
```
Do I need estate planning with my current net worth?
```

**Integrated:**
```
I'm thinking of selling my business for $5M. What should I consider?
```

### 3. Review Recommendations

After each query, you'll see:
- **AI Response**: Comprehensive recommendation with citations [doc_id]
- **Analysis Breakdown**: 
  - Tax strategies and considerations
  - Investment allocation chart
  - Estate planning triggers and structures
- **Supporting Evidence**: Source documents used in analysis

## Verify Everything Works

### Backend Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Test API Directly

```bash
curl -X POST http://localhost:8000/session/new
# Expected: {"session_id":"uuid-here"}
```

## Common Issues

### Issue: "Module 'faiss' not found"

**Solution:**
```bash
pip install faiss-cpu
```

### Issue: "Vector stores not initialized"

**Cause:** Missing corpus files

**Solution:** Verify these files exist:
```
backend/data/corpus/tax_knowledge.jsonl
backend/data/corpus/investment_knowledge.jsonl
backend/data/corpus/estate_knowledge.jsonl
```

They should already be included in the project.

### Issue: "Invalid API key"

**Solution:**
1. Check your `.env` file has the correct key
2. Verify key is active and has credits
3. Confirm `LLM_PROVIDER` matches the key you're using

### Issue: Frontend can't reach backend

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/.env`
3. Ensure ports 5173 (frontend) and 8000 (backend) are free

### Issue: npm install fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

### Customize Knowledge Base

Add more financial planning knowledge:

```bash
# Edit corpus files
nano backend/data/corpus/tax_knowledge.jsonl
```

Add entries in JSONL format:
```json
{"doc_id": "tax_013", "category": "retirement", "text": "Your knowledge here..."}
```

Restart backend to rebuild vector stores.

### Switch LLM Provider

Edit `backend/.env`:
```
LLM_PROVIDER=gemini  # or openai, groq
```

Restart backend server.

### Customize Frontend Styling

Edit `frontend/src/index.css` and modify CSS variables:
```css
:root {
  --primary-color: #your-color;
}
```

## Getting API Keys

### OpenAI (Recommended)
1. Visit https://platform.openai.com/api-keys
2. Create account and add payment method
3. Generate API key
4. Cost: ~$0.50-2.00 per session (GPT-4o-mini)

### Google Gemini
1. Visit https://aistudio.google.com/app/apikey
2. Create Google Cloud account
3. Generate API key
4. Cost: Free tier available, very low cost

### Groq (Fastest)
1. Visit https://console.groq.com
2. Create account (free)
3. Generate API key
4. Cost: Free tier available

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- Backend: `--reload` flag automatically reloads on code changes
- Frontend: Vite HMR updates instantly

### Debugging

**Backend logs:**
```bash
# Terminal running uvicorn shows all requests and errors
```

**Frontend console:**
```
Open browser DevTools → Console tab
```

**API testing:**
```bash
# Use curl or Postman
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"test query"}'
```

### Adding Features

1. **New domain module**: Create file in `backend/app/modules/`
2. **New API endpoint**: Add route in `backend/app/main.py`
3. **New UI component**: Create file in `frontend/src/components/`
4. **New visualization**: Use Recharts in BreakdownPanel

## Performance Notes

- **First query**: 3-5 seconds (RAG retrieval + LLM inference)
- **Subsequent queries**: 2-3 seconds
- **Profile creation**: <1 second
- **RAG indexing**: ~2 seconds on startup

## Security Reminder

- Never commit `.env` files
- Use environment variables for secrets
- This is not production-ready (no auth, in-memory storage)
- For production: Add JWT auth, database, rate limiting, audit logs

## Support & Troubleshooting

If you encounter issues:

1. Check both backend and frontend terminals for errors
2. Verify all dependencies installed: `pip list` and `npm list`
3. Test backend independently: `curl http://localhost:8000/health`
4. Review detailed logs in terminal output
5. See [Backend README](./backend/README.md) or [Frontend README](./frontend/README.md)

## What to Try First

After setup, try this end-to-end test:

1. **Complete intake form** with sample data
2. **Ask**: "I'm 45 years old with $850K income and $5M in assets. What should I focus on?"
3. **Observe**:
   - Router selects all 3 modules
   - Each module retrieves relevant knowledge
   - Synthesizer creates integrated recommendation
   - UI shows breakdown with charts
   - Evidence panel displays source citations

You should see a comprehensive plan covering tax optimization, investment allocation, and estate planning with proper citations like [tax_001], [inv_005], [est_003].

## Ready to Go!

You now have a fully functional Family Office AI Agent running locally. Start by completing the intake form and asking your first question.

Happy planning! 🚀
