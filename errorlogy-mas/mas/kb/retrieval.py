"""Pipeline KB retrieval — hybrid Zvec search with safe fallbacks."""

from __future__ import annotations

import importlib.util
import logging
from typing import TYPE_CHECKING

from ..config import (
    KB_COLLECTION,
    KB_ENABLED,
    KB_INGEST_ON_COMPLETE,
    KB_INGEST_ON_SCOUT,
    KB_QUERY_MODE,
    KB_TOPK,
    KB_ZVEC_PATH,
)
from ..schemas.case import GovernanceCase

if TYPE_CHECKING:
    from ..schemas.analysis import ModeScore, WMSResult

logger = logging.getLogger(__name__)

_zvec_available: bool | None = None
_retriever: "KBRetriever | None" = None


def zvec_installed() -> bool:
    global _zvec_available
    if _zvec_available is None:
        _zvec_available = importlib.util.find_spec("zvec") is not None
    return _zvec_available


def kb_active() -> bool:
    return KB_ENABLED and zvec_installed()


def build_case_query(
    case: GovernanceCase,
    *,
    wms_result: "WMSResult | None" = None,
    top_modes: list["ModeScore"] | None = None,
) -> str:
    """Compose a hybrid-search query from whatever pipeline context is available."""
    parts: list[str] = []
    if case.title:
        parts.append(case.title)
    if case.description:
        parts.append(case.description)
    if case.country:
        parts.append(case.country)
    if case.year:
        parts.append(str(case.year))

    for sig in case.weak_signals[:6]:
        if sig.description:
            parts.append(sig.description)

    if wms_result is not None and wms_result.early_warning_hypothesis:
        parts.append(wms_result.early_warning_hypothesis)

    for mode in (top_modes or [])[:5]:
        parts.append(f"{mode.mode_id} {mode.name}")

    text = " ".join(p.strip() for p in parts if p and p.strip())
    if not text and case.source_text:
        text = case.source_text[:800]
    return text[:2000]


def format_kb_context(hits) -> str:
    if not hits:
        return ""
    lines = [
        "KNOWLEDGE BASE CONTEXT (reference snippets only; hypotheses, not verified evidence):"
    ]
    for i, hit in enumerate(hits, start=1):
        snippet = (hit.text or "").replace("\n", " ").strip()[:600]
        if not snippet:
            continue
        lines.append(f"  {i}. [id={hit.id}, score={hit.score:.3f}] {snippet}")
    return "\n".join(lines) if len(lines) > 1 else ""


def build_index_document(
    case: GovernanceCase,
    *,
    public_card: str = "",
) -> tuple[str, str]:
    doc_id = f"case:{case.case_id}"
    chunks = [case.title, case.description]
    if public_card:
        chunks.append(public_card[:2000])
    text = "\n\n".join(c for c in chunks if c and c.strip())
    return doc_id, text


class KBRetriever:
    """Lazy ZvecStore wrapper; no-op when KB is disabled or zvec is missing."""

    def __init__(self) -> None:
        self._store = None
        self._ready = False
        self._available = kb_active()

    @property
    def available(self) -> bool:
        return self._available

    def _ensure_store(self):
        if not self._available or self._ready:
            return
        try:
            from .zvec_store import ZvecStore

            self._store = ZvecStore(path=KB_ZVEC_PATH, collection_name=KB_COLLECTION)
            self._store.open()
            self._store.ensure_fts_index()
            self._store.ensure_vector_index()
            self._ready = True
        except Exception as exc:
            logger.debug("KB store unavailable: %s", exc)
            self._available = False
            self._store = None
            self._ready = True

    def retrieve(self, query_text: str) -> str:
        if not self._available or not (query_text or "").strip():
            return ""
        self._ensure_store()
        if self._store is None:
            return ""
        try:
            hits = self._store.query(
                query_text,
                topk=KB_TOPK,
                mode=KB_QUERY_MODE,  # type: ignore[arg-type]
            )
            return format_kb_context(hits)
        except Exception as exc:
            logger.debug("KB query failed: %s", exc)
            return ""

    def index_case(
        self,
        case: GovernanceCase,
        *,
        public_card: str = "",
    ) -> bool:
        if not self._available:
            return False
        doc_id, text = build_index_document(case, public_card=public_card)
        if not text.strip():
            return False
        self._ensure_store()
        if self._store is None:
            return False
        try:
            self._store.add_texts([(doc_id, text)])
            return True
        except Exception as exc:
            logger.debug("KB index failed: %s", exc)
            return False


def get_kb_retriever() -> KBRetriever:
    global _retriever
    if _retriever is None:
        _retriever = KBRetriever()
    return _retriever


def attach_kb_context(
    case: GovernanceCase,
    *,
    wms_result: "WMSResult | None" = None,
    top_modes: list["ModeScore"] | None = None,
) -> tuple[GovernanceCase, str]:
    """Query KB and store formatted context on the case metadata."""
    retriever = get_kb_retriever()
    query = build_case_query(case, wms_result=wms_result, top_modes=top_modes)
    kb_context = retriever.retrieve(query)
    if not kb_context:
        return case, ""

    meta = dict(case.metadata or {})
    meta["kb_context"] = kb_context
    meta["kb_query"] = query[:500]
    return case.model_copy(update={"metadata": meta}), kb_context


def maybe_ingest_scout(case: GovernanceCase) -> None:
    if not KB_INGEST_ON_SCOUT:
        return
    get_kb_retriever().index_case(case)


def maybe_ingest_complete(case: GovernanceCase, public_card: str = "") -> None:
    if not KB_INGEST_ON_COMPLETE:
        return
    get_kb_retriever().index_case(case, public_card=public_card)
