import os
import json
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings

# Directory for persisted FAISS indices (load from here on startup; rebuild and save when missing)
FAISS_INDEX_DIR = "data/faiss_index"


class VectorStoreManager:
    def __init__(self, corpus_dir: str = "data/corpus", index_dir: str = FAISS_INDEX_DIR):
        self.corpus_dir = corpus_dir
        self.index_dir = index_dir
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self.stores: Dict[str, FAISS] = {}

    def _index_path(self, module: str) -> str:
        return os.path.join(self.index_dir, module)

    def _index_exists(self, module: str) -> bool:
        path = self._index_path(module)
        # FAISS.save_local writes index.faiss and index.pkl
        return os.path.exists(os.path.join(path, "index.faiss"))

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
        os.makedirs(self.index_dir, exist_ok=True)

        for module in modules:
            corpus_path = os.path.join(self.corpus_dir, f"{module}_knowledge.jsonl")
            index_path = self._index_path(module)

            if self._index_exists(module):
                try:
                    # Older langchain_community versions do not support allow_dangerous_deserialization.
                    # Since these indices are built locally by this app, loading without that flag is acceptable.
                    self.stores[module] = FAISS.load_local(index_path, self.embeddings)
                    print(f"Loaded FAISS index for {module} (from cache)")
                except Exception as e:
                    print(f"Failed to load cached index for {module}: {e}. Rebuilding...")
                    self._build_and_save(module, corpus_path, index_path)
            elif os.path.exists(corpus_path):
                self._build_and_save(module, corpus_path, index_path)
            else:
                print(f"Warning: Corpus not found for {module} at {corpus_path}")

    def _build_and_save(self, module: str, corpus_path: str, index_path: str):
        docs = self.load_jsonl_corpus(corpus_path)
        self.stores[module] = FAISS.from_documents(docs, self.embeddings)
        os.makedirs(index_path, exist_ok=True)
        self.stores[module].save_local(index_path)
        print(f"Built and saved FAISS index for {module} ({len(docs)} documents)")
    
    def get_retriever(self, module: str, k: int = None):
        if module not in self.stores:
            raise ValueError(f"Module '{module}' not initialized")
        
        k = k or settings.rag_top_k
        return self.stores[module].as_retriever(search_kwargs={"k": k})

vector_store_manager = VectorStoreManager()
