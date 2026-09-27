from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os

load_dotenv(override=True)

model_name = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
model_provider = os.getenv("MODEL_PROVIDER", "groq")
max_tokens = os.getenv("MAX_TOKENS", 800)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ORDER_SESSION_TTL_SECONDS = int(os.getenv("ORDER_SESSION_TTL_SECONDS", "3600"))


llm = init_chat_model(model=model_name, model_provider=model_provider, max_tokens=max_tokens)

print(llm.model_name)