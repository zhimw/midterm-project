#!/usr/bin/env python3

import sys
import os
from pathlib import Path

def check_file(path: str, description: str) -> bool:
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} MISSING: {path}")
        return False

def check_python_imports() -> bool:
    print("\n📦 Checking Python dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "openai",
        "langchain",
        "faiss",
        "sentence_transformers"
    ]
    
    all_ok = True
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ {pkg} - Run: pip install {pkg}")
            all_ok = False
    
    return all_ok

def main():
    print("="*80)
    print("  Family Office AI Agent - Installation Verification")
    print("="*80)
    
    checks = []
    
    print("\n📁 Checking project structure...")
    
    checks.append(check_file("backend/app/main.py", "Backend main"))
    checks.append(check_file("backend/requirements.txt", "Backend requirements"))
    checks.append(check_file("backend/.env.example", "Backend env example"))
    checks.append(check_file("backend/data/corpus/tax_knowledge.jsonl", "Tax corpus"))
    checks.append(check_file("backend/data/corpus/investment_knowledge.jsonl", "Investment corpus"))
    checks.append(check_file("backend/data/corpus/estate_knowledge.jsonl", "Estate corpus"))
    
    checks.append(check_file("frontend/package.json", "Frontend package.json"))
    checks.append(check_file("frontend/src/App.tsx", "Frontend App"))
    checks.append(check_file("frontend/src/components/IntakeForm.tsx", "Intake Form"))
    checks.append(check_file("frontend/src/components/ChatInterface.tsx", "Chat Interface"))
    
    checks.append(check_file("README.md", "Project README"))
    checks.append(check_file("QUICKSTART.md", "Quick Start Guide"))
    
    env_exists = os.path.exists("backend/.env")
    if not env_exists:
        print(f"\n⚠️  backend/.env not found")
        print(f"   Run: cp backend/.env.example backend/.env")
        print(f"   Then edit backend/.env with your API keys")
    
    os.chdir("backend")
    try:
        import_ok = check_python_imports()
        checks.append(import_ok)
    except Exception as e:
        print(f"❌ Could not check imports: {e}")
        checks.append(False)
    os.chdir("..")
    
    print("\n" + "="*80)
    if all(checks):
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 Ready to start:")
        print("   Terminal 1: cd backend && uvicorn app.main:app --reload")
        print("   Terminal 2: cd frontend && npm run dev")
        print("   Browser: http://localhost:5173")
    else:
        print("❌ SOME CHECKS FAILED")
        print("\n   Please fix the issues above before starting.")
        sys.exit(1)
    print("="*80)

if __name__ == "__main__":
    main()
