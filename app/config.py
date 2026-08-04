import io
import os
import sys
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("NVIDIA_API_KEY")

NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/meta/llama-3.1-70b-instruct")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
PORT = int(os.getenv("PORT", 8000))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://precios:precios2024@db:5432/pricepulse")
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "4"))
