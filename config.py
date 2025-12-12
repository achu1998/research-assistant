import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
# Supports "ollama" or "cloud" (OpenAI/Anthropic if you add those clients later)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama") 
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Recommended: Llama 3 70B or Qwen 2.5 72B for high-level research reasoning
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b") 

# Research Loop Settings
MAX_REFINEMENT_LOOPS = int(os.getenv("MAX_REFINEMENT_LOOPS", 5))  # Prevent infinite loops
SEARCH_RESULTS_PER_ITERATION = int(os.getenv("SEARCH_RESULTS_PER_ITERATION", 5))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.85)) # How strict the novelty check is