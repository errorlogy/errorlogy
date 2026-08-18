import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
TAXONOMY_PATH = ROOT / "data" / "errorlogy_unified_taxonomy_v16.json"


def _env_bool(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


# ── LLM providers ──────────────────────────────────────────────────
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY     = os.environ.get("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
GOOGLE_API_KEY     = os.environ.get("GOOGLE_API_KEY", "")
DEEPSEEK_API_KEY   = os.environ.get("DEEPSEEK_API_KEY", "")
GROQ_API_KEY       = os.environ.get("GROQ_API_KEY", "")
KIMI_API_KEY       = os.environ.get("KIMI_API_KEY", "")
ZAI_API_KEY        = os.environ.get("ZAI_API_KEY", "")
EXA_API_KEY        = os.environ.get("EXA_API_KEY", "")
EXA_SEARCH_TYPE    = os.environ.get("EXA_SEARCH_TYPE", "auto").strip() or "auto"
EXA_AGENT_MODE     = _env_bool("EXA_AGENT_MODE")
EXA_AGENT_EFFORT   = os.environ.get("EXA_AGENT_EFFORT", "minimal").strip() or "minimal"
EXA_PREFERRED      = _env_bool("EXA_PREFERRED")

# ── US gov ingest (optional) ─────────────────────────────────────────
GOVINFO_API_KEY         = os.environ.get("GOVINFO_API_KEY", "")
COURTLISTENER_API_TOKEN = os.environ.get("COURTLISTENER_API_TOKEN", "")
LEGISCAN_API_KEY        = os.environ.get("LEGISCAN_API_KEY", "")

# ── OAuth / Auth ────────────────────────────────────────────────────
GOOGLE_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID     = os.environ.get("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "")
TELEGRAM_BOT_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
JWT_SECRET           = os.environ.get("JWT_SECRET", "errorlogy-dev-secret-change-in-prod")

# ── Alpha propagation ───────────────────────────────────────────────
ALPHA_STEPS    = 5
ALPHA_DAMPING  = 0.85
ALPHA_THRESHOLD = 0.05

MAX_TOKENS = 4096

# ── Knowledge base (Zvec, optional) ─────────────────────────────────
KB_ENABLED = os.environ.get("KB_ENABLED", "true").strip().lower() not in ("0", "false", "no", "off")
KB_ZVEC_PATH = os.environ.get("KB_ZVEC_PATH", str(ROOT / ".data" / "zvec_kb"))
KB_COLLECTION = os.environ.get("KB_COLLECTION", "kb")
KB_TOPK = int(os.environ.get("KB_TOPK", "5"))
KB_QUERY_MODE = os.environ.get("KB_QUERY_MODE", "hybrid")
KB_INGEST_ON_COMPLETE = _env_bool("KB_INGEST_ON_COMPLETE")
KB_INGEST_ON_SCOUT = _env_bool("KB_INGEST_ON_SCOUT")


class Config:
    """Single config object passed to router builder."""
    ANTHROPIC_API_KEY  = ANTHROPIC_API_KEY
    OPENAI_API_KEY     = OPENAI_API_KEY
    OPENROUTER_API_KEY = OPENROUTER_API_KEY
    GOOGLE_API_KEY     = GOOGLE_API_KEY
    DEEPSEEK_API_KEY   = DEEPSEEK_API_KEY
    GROQ_API_KEY       = GROQ_API_KEY
    KIMI_API_KEY       = KIMI_API_KEY
    ZAI_API_KEY        = ZAI_API_KEY

    def available_providers(self) -> list[str]:
        out = []
        if self.ANTHROPIC_API_KEY:  out.append("anthropic")
        if self.OPENROUTER_API_KEY: out.append("openrouter")
        if self.OPENAI_API_KEY:     out.append("openai")
        if self.GOOGLE_API_KEY:     out.append("google")
        if self.DEEPSEEK_API_KEY:   out.append("deepseek")
        if self.GROQ_API_KEY:       out.append("groq")
        if self.KIMI_API_KEY:       out.append("kimi")
        if self.ZAI_API_KEY:        out.append("zai")
        return out
