from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os
from pathlib import Path

load_dotenv(override=True)

_BASE_DIR = Path(__file__).resolve().parent

model_name = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
model_provider = os.getenv("MODEL_PROVIDER", "groq")
max_tokens = os.getenv("MAX_TOKENS", 800)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ORDER_SESSION_TTL_SECONDS = int(os.getenv("ORDER_SESSION_TTL_SECONDS", "3600"))

RAG_DATA_DIR = Path(os.getenv("RAG_DATA_DIR", str(_BASE_DIR / "rag_data")))
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
# Dedicated FAQ index (384-dim for MiniLM). Keep separate from other indexes.
PINECONE_INDEX_NAME = os.getenv("PINECONE_FAQ_INDEX_NAME") or os.getenv(
    "PINECONE_INDEX_NAME", "savostore-faq"
)
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_URL = os.getenv("PINECONE_URL", "")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "savostore_faq")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))
HF_TOKEN = os.getenv("HF_TOKEN", "")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))

llm = init_chat_model(model=model_name, model_provider=model_provider, max_tokens=max_tokens)

print(llm.model_name)
