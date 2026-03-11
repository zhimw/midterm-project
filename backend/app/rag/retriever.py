from typing import List, Dict, Any
from langchain_core.documents import Document
from app.rag.vector_store import vector_store_manager
from app.config import settings

class RAGRetriever:
    def __init__(self):
        self.vector_store_manager = vector_store_manager
    
    def retrieve(self, query: str, module: str, k: int = None) -> List[Document]:
        k = k or settings.rag_top_k
        retriever = self.vector_store_manager.get_retriever(module, k=k)
        return retriever.invoke(query)
    
    def retrieve_multi_module(self, query: str, modules: List[str], k: int = None) -> Dict[str, List[Document]]:
        results = {}
        for module in modules:
            try:
                results[module] = self.retrieve(query, module, k=k)
            except Exception as e:
                print(f"Error retrieving from {module}: {e}")
                results[module] = []
        return results
    
    def format_evidence(self, docs: List[Document], max_chars: int = 300) -> List[Dict[str, Any]]:
        evidence = []
        for doc in docs:
            snippet = doc.page_content[:max_chars].strip()
            if len(doc.page_content) > max_chars:
                snippet += "..."
            
            evidence.append({
                "doc_id": doc.metadata.get("doc_id", "N/A"),
                "category": doc.metadata.get("category", "N/A"),
                "snippet": snippet,
                "full_text": doc.page_content
            })
        return evidence
    
    def build_context_prompt(self, docs: List[Document]) -> str:
        ctx_blocks = []
        for d in docs:
            doc_id = d.metadata.get("doc_id", "unknown")
            ctx_blocks.append(f"[{doc_id}]\n{d.page_content.strip()}")
        return "\n\n".join(ctx_blocks)

rag_retriever = RAGRetriever()
