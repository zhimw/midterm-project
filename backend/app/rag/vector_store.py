import os
import json
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings

class VectorStoreManager:
    def __init__(self, corpus_dir: str = "data/corpus"):
        self.corpus_dir = corpus_dir
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self.stores: Dict[str, FAISS] = {}
        
    def load_jsonl_corpus(self, path: str) -> List[Document]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Corpus file not found: {path}")
        
        docs: List[Document] = []
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                
                if "doc_id" not in obj or "text" not in obj:
                    raise ValueError(f"Invalid JSONL at line {line_no}: missing doc_id or text.")
                
                text = obj["text"]
                metadata = {k: v for k, v in obj.items() if k != "text"}
                docs.append(Document(page_content=text, metadata=metadata))
        
        if not docs:
            raise ValueError(f"Corpus loaded 0 documents from {path}")
        return docs
    
    def initialize_stores(self):
        modules = ["tax", "investment", "estate"]
        
        for module in modules:
            corpus_path = os.path.join(self.corpus_dir, f"{module}_knowledge.jsonl")
            if os.path.exists(corpus_path):
                docs = self.load_jsonl_corpus(corpus_path)
                self.stores[module] = FAISS.from_documents(docs, self.embeddings)
                print(f"Loaded {len(docs)} documents for {module} module")
            else:
                print(f"Warning: Corpus not found for {module} at {corpus_path}")
    
    def get_retriever(self, module: str, k: int = None):
        if module not in self.stores:
            raise ValueError(f"Module '{module}' not initialized")
        
        k = k or settings.rag_top_k
        return self.stores[module].as_retriever(search_kwargs={"k": k})

vector_store_manager = VectorStoreManager()
