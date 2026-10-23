import os, re, json, time, html, hashlib, platform
from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime, timezone
from importlib.metadata import version, PackageNotFoundError
import numpy as np
import pandas as pd
import requests
from rank_bm25 import BM25Okapi
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape

SEED = 42
CLAIM_ID = "ABX-001"
CLAIM_TO_CHECK = "Antibiotics do not treat viral infections."
MAX_RESULTS_PER_QUERY = 25
MAX_PAPERS_TO_RANK = 20
MAX_EVIDENCE_PASSAGES = 6
REQUEST_TIMEOUT_SECONDS = 30
RUN_BENCHMARK = False
BENCHMARK_LIMIT = None  # Set to 3 for a quicker smoke test.
# True means each benchmark claim attempts Gemini when a key is available.
# Set False to save API calls; the output will clearly state that LLM was disabled.
BENCHMARK_USE_LLM = True
NLI_MODEL_NAME = "gemma-4-26b-a4b-it"
EMBEDDING_MODEL_NAME = "BM25-only (no local embeddings)"
# Override with GEMINI_MODEL_NAME environment variable if your API account uses another supported model.
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemma-4-26b-a4b-it")
# Fail over only on transient service/capacity failures; first model remains the preferred choice.
GEMINI_FALLBACK_MODELS = [
    m.strip() for m in os.environ.get(
        "GEMINI_FALLBACK_MODELS",
        ""
    ).split(",") if m.strip() and m.strip() != GEMINI_MODEL_NAME
]
GEMINI_MAX_RETRIES_PER_MODEL = 2
GEMINI_BACKOFF_BASE_SECONDS = 1.0
GEMINI_BACKOFF_MAX_SECONDS = 4.0

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip()
try:
    from kaggle_secrets import UserSecretsClient
    if not GEMINI_API_KEY:
        try:
            GEMINI_API_KEY = UserSecretsClient().get_secret("GEMINI_API_KEY").strip()
        except Exception as secret_exc:
            print("Kaggle secret unavailable; checking environment variables. Detail:", str(secret_exc)[:180])
except Exception:
    pass
LLM_ENABLED = bool(GEMINI_API_KEY)
DEVICE = "API-only (no local model)"
OUT_DIR = Path(os.environ.get("ABX_OUTPUT_DIR", "outputs"))
OUT_DIR.mkdir(parents=True, exist_ok=True)
np.random.seed(SEED)

def package_version(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"

RUN_STARTED_UTC = datetime.now(timezone.utc).isoformat()
ENVIRONMENT = {
    "python": platform.python_version(), "pandas": package_version("pandas"),
    "numpy": package_version("numpy"), "requests": package_version("requests"),
    "google-genai": package_version("google-genai"),
    "rank_bm25": package_version("rank-bm25"),
    
    "inference_mode": DEVICE, "nli_model": NLI_MODEL_NAME,
    "embedding_model": EMBEDDING_MODEL_NAME,
    "llm_enabled": LLM_ENABLED,
    "llm_model": GEMINI_MODEL_NAME if LLM_ENABLED else "disabled_no_api_key",
    "llm_fallback_models": GEMINI_FALLBACK_MODELS,
    "benchmark_use_llm": BENCHMARK_USE_LLM,
    "seed": SEED, "run_started_utc": RUN_STARTED_UTC
}
print(json.dumps(ENVIRONMENT, indent=2))

# Google GenAI SDK client: inference is hosted; no local model weights are downloaded.
try:
    from google import genai
except Exception:
    genai = None

def get_genai_client():
    key = (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or GEMINI_API_KEY or "").strip()
    if not key:
        raise RuntimeError("Missing Google API key. Set GOOGLE_API_KEY or GEMINI_API_KEY.")
    if genai is None:
        raise RuntimeError("google-genai is not installed. Run pip install -r requirements.txt.")
    return genai.Client(api_key=key)
