import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
LLM_URL  = os.getenv("LLM_URL",  f"{BASE_URL}/v1/chat/completions")
MODEL    = os.getenv("MODEL", "gemma")
