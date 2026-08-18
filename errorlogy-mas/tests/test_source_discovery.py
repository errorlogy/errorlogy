"""Source discovery (Exa / web search) for pre-pipeline enrichment."""

from unittest.mock import patch

from mas.ingest.source_discovery import (
    build_discovery_query,
    enrich_source_bundle,
    format_source_bundle_section,
)


def test_build_discovery_query_from_title():
    q = build_discovery_query(title="Horizon IT scandal", country="UK", year=1999)
    assert "Horizon" in q
    assert "1999" in q
    assert "investigation" in q.lower() or "inquiry" in q.lower()


def test_format_source_bundle_section():
    hits = [{
        "title": "Inquiry report",
        "url": "https://example.com/r",
        "text": "Government schedule pressure led to safety override " * 8,
    }]
    section = format_source_bundle_section(hits, provider="exa")
    assert "ADDITIONAL SOURCES" in section
    assert "https://example.com/r" in section


def test_enrich_source_bundle_mock(monkeypatch):
    monkeypatch.setenv("EXA_API_KEY", "test-key")
    from mas.ingest.fetchers import exa as exa_mod
    exa_mod._client.cache_clear()

    hit = {
        "doc_id": "exa-1",
        "source": "exa",
        "source_type": "web_search",
        "url": "https://example.com/inquiry",
        "title": "Parliamentary inquiry",
        "country": "UK",
        "text": "Post Office prosecuted subpostmasters based on faulty Horizon data " * 6,
    }

    with patch("mas.ingest.source_discovery.discover_sources", return_value=([hit], "exa")):
        enriched, hits, provider = enrich_source_bundle(
            "Seed text about Horizon prosecutions.",
            title="Horizon scandal",
            country="UK",
            year=1999,
        )

    assert provider == "exa"
    assert len(hits) == 1
    assert "ADDITIONAL SOURCES" in enriched
    assert "Seed text" in enriched


def test_orchestrator_enrich_sources_mock(monkeypatch):
    monkeypatch.setenv("EXA_API_KEY", "test-key")
    from mas.orchestrator import Orchestrator

    hit = {
        "title": "Report",
        "url": "https://example.com/r",
        "text": "Regulatory failure and whistleblower suppression documented " * 8,
    }

    with patch(
        "mas.ingest.source_discovery.enrich_source_bundle",
        return_value=("enriched text " * 40, [hit], "exa"),
    ):
        orch = Orchestrator(init_llm=False)
        result = orch.run_from_text(
            case_id="TEST-ENRICH-01",
            raw_text="Short seed about governance failure.",
            title="Test case",
            country="UK",
            year=2020,
            engine_only=True,
            enrich_sources=True,
            verbose=False,
        )

    assert result.metadata.get("source_discovery", {}).get("hits") == 1
