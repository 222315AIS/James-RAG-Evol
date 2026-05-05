# ── .env 파일 자동 로드 (있으면) ────────────────────────────────
import os
_env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_file):
    try:
        with open(_env_file, encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if not _line or _line.startswith("#") or "=" not in _line:
                    continue
                _k, _v = _line.split("=", 1)
                _k, _v = _k.strip(), _v.strip().strip('"').strip("'")
                if _k and _v and _k not in os.environ:
                    os.environ[_k] = _v
        print(f"[CONFIG] .env 파일 로드: {_env_file}")
    except Exception as _e:
        print(f"[CONFIG] .env 로드 실패: {_e}")

"""
PROJECT JAMES - Config (Phase 4)
[P4-CFG-1] API_KEY from environment variable
"""
import os
import pytesseract

# Base directories
BASE_DIR   = r"C:\Project\james prototype"
RAW_DIR    = os.path.join(BASE_DIR, "raw")
WIKI_DIR   = os.path.join(BASE_DIR, "wiki")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# Tesseract OCR
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Ollama / Gemma
OLLAMA_PATH    = r"C:\Users\hyunn\AppData\Local\Programs\Ollama\ollama.exe"
GEMMA_MODEL    = "gemma4:e4b"
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

# ChromaDB
CHROMA_COLLECTION = "james_prototype"

# [P4-CFG-1] API_KEY - environment variable required
# How to set:
#   CMD:        set JAMES_API_KEY=your_key_here
#   PowerShell: $env:JAMES_API_KEY="your_key_here"
API_KEY = os.environ.get("JAMES_API_KEY", "")
if not API_KEY:
    print("[CONFIG] WARNING: JAMES_API_KEY not set - using dev fallback")
    API_KEY = "dev_only_change_me"

MAX_UPLOAD_MB    = 100
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# Upload / Poppler
# NOTE: Set POPPLER_PATH to your actual poppler bin directory
# Example: r"C:\poppler\Library\bin"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
POPPLER_PATH  = os.environ.get(
    "JAMES_POPPLER_PATH",
    r"C:\Users\hyunn\OneDrive\Desktop\Release-25.12.0-0\poppler-25.12.0\Library\bin"
)

print(f"[CONFIG] PROJECT JAMES ready")
print(f"[CONFIG] BASE_DIR: {BASE_DIR}")
print(f"[CONFIG] API_KEY source: {'env:JAMES_API_KEY' if os.environ.get('JAMES_API_KEY') else 'dev fallback'}")

# ── 웹 검색 API (3-E) ───────────────────────────────────────────
# Tavily: https://tavily.com → 무료 1,000회/월
# 설정: 환경변수 TAVILY_API_KEY=tvly-xxxx 또는 .env 파일
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
if TAVILY_API_KEY:
    print(f"[CONFIG] Tavily 검색 활성화 (key: {TAVILY_API_KEY[:8]}...)")
else:
    print("[CONFIG] Tavily 키 없음 → DuckDuckGo 검색 사용")
