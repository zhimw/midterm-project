import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def demo():
    print_section("Family Office AI Agent - Demo")
    
    print("1️⃣  Creating new session...")
    response = requests.post(f"{BASE_URL}/session/new")
    session_id = response.json()["session_id"]
    print(f"   Session ID: {session_id}")
    
    print("\n2️⃣  Creating user profile...")
    profile = {
        "session_id": session_id,
        "profile": {
            "age": 48,
            "income": 950000,
            "filing_status": "married",
            "state": "CA",
            "assets": {
                "cash": 300000,
                "stocks": 3500000,
                "bonds": 800000,
                "real_estate": 2500000,
                "business": 1500000
            },
            "family": {
                "marital_status": "married",
                "children": 3
            },
            "life_events": ["birth"],
            "goals": ["retirement planning", "college funding", "wealth preservation"],
            "investment_goals": ["tax efficiency", "capital appreciation"],
            "estate_goals": ["minimize estate taxes", "wealth transfer"],
            "risk_tolerance": "moderate",
            "time_horizon": "long-term"
        }
    }
    
    response = requests.post(f"{BASE_URL}/profile/create", json=profile)
    print(f"   Profile created: {response.json()['message']}")
    
    queries = [
        "What tax strategies should I consider given my income and location in California?",
        "How should I allocate my investment portfolio for tax efficiency?",
        "With my estate value, what trust structures should I consider?"
    ]
    
    for i, query in enumerate(queries, 1):
        print_section(f"Query {i}")
        print(f"Question: {query}\n")
        
        chat_request = {
            "session_id": session_id,
            "message": query
        }
        
        print("   🤔 Processing query...")
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/chat", json=chat_request)
        elapsed = time.time() - start_time
        
        result = response.json()
        
        print(f"   ⏱️  Response time: {elapsed:.2f}s")
        print(f"   📊 Modules used: {', '.join(result['modules_used'])}")
        
        print("\n📝 RECOMMENDATION:")
        print("-" * 80)
        print(result["response"][:800] + "..." if len(result["response"]) > 800 else result["response"])
        
        if result.get("breakdown"):
            print("\n📊 BREAKDOWN:")
            print(json.dumps(result["breakdown"], indent=2)[:500])
        
        print(f"\n🔍 Evidence sources: {len(result.get('evidence', []))} documents")
        
        if i < len(queries):
            time.sleep(1)
    
    print_section("Demo Complete")
    print(f"Session ID: {session_id}")
    print(f"View full history at: {BASE_URL}/history/{session_id}")

if __name__ == "__main__":
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            demo()
        else:
            print("❌ Backend is not responding correctly")
    except requests.exceptions.RequestException:
        print("❌ Backend is not running!")
        print("   Start it with: cd backend && uvicorn app.main:app --reload")
