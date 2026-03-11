#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    print("Testing imports...")
    try:
        from app.config import settings
        print("✅ Config")
        
        from app.llm.client import LLMClient
        print("✅ LLM Client")
        
        from app.rag.vector_store import VectorStoreManager
        print("✅ Vector Store Manager")
        
        from app.rag.retriever import RAGRetriever
        print("✅ RAG Retriever")
        
        from app.modules.tax import TaxOptimizationModule
        print("✅ Tax Module")
        
        from app.modules.investment import InvestmentAllocationModule
        print("✅ Investment Module")
        
        from app.modules.estate import EstatePlanningModule
        print("✅ Estate Module")
        
        from app.agent.router import AgentRouter
        print("✅ Router")
        
        from app.agent.synthesizer import RecommendationSynthesizer
        print("✅ Synthesizer")
        
        from app.agent.orchestrator import FamilyOfficeAgent
        print("✅ Orchestrator")
        
        from app.memory.store import ConversationMemory
        print("✅ Memory Store")
        
        from app.models import UserProfile, ChatRequest, ChatResponse
        print("✅ Models")
        
        print("\n✅ All imports successful!")
        return True
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        return False

def test_vector_store():
    print("\nTesting vector store initialization...")
    try:
        from app.rag.vector_store import vector_store_manager
        
        corpus_dir = os.path.join(os.path.dirname(__file__), "data", "corpus")
        vector_store_manager.corpus_dir = corpus_dir
        
        vector_store_manager.initialize_stores()
        
        print(f"✅ Vector stores initialized")
        print(f"   Modules: {list(vector_store_manager.stores.keys())}")
        return True
    except Exception as e:
        print(f"❌ Vector store initialization failed: {e}")
        return False

def test_llm_client():
    print("\nTesting LLM client configuration...")
    try:
        from app.config import settings
        
        print(f"   Provider: {settings.llm_provider}")
        
        has_key = False
        if settings.llm_provider == "openai" and settings.openai_api_key:
            has_key = True
        elif settings.llm_provider == "gemini" and settings.gemini_api_key:
            has_key = True
        elif settings.llm_provider == "groq" and settings.groq_api_key:
            has_key = True
        
        if has_key:
            print(f"✅ API key configured for {settings.llm_provider}")
        else:
            print(f"⚠️  No API key found for {settings.llm_provider}")
            print(f"   Set {settings.llm_provider.upper()}_API_KEY in .env")
        
        return True
    except Exception as e:
        print(f"❌ LLM client test failed: {e}")
        return False

def main():
    print("="*80)
    print("  Family Office AI Agent - Backend System Test")
    print("="*80)
    print()
    
    results = []
    
    results.append(test_imports())
    results.append(test_vector_store())
    results.append(test_llm_client())
    
    print("\n" + "="*80)
    if all(results):
        print("✅ ALL TESTS PASSED")
        print("\nBackend is ready to run:")
        print("   uvicorn app.main:app --reload")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix issues above before starting the server.")
        sys.exit(1)
    print("="*80)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()
