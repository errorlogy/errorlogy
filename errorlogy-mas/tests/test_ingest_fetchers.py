"""Ingest fetcher tests (no live network)."""

from unittest.mock import MagicMock, patch

from mas.db import init_db, list_raw_documents
from mas.ingest.fetchers import rss, url
from mas.ingest.fetchers._common import html_to_text, normalize_hit
from mas.ingest import ingest_batch, ingest_url, run_rss_fetch, fetcher_status


SAMPLE_HTML = """
<html><head><title>Test Report</title></head>
<body><p>Government management overruled engineers on safety launch decision
under intense schedule pressure from political leadership in 2024.</p>
<p>Additional paragraphs describe regulatory capture and whistleblower suppression
across multiple agencies during the oversight review process.</p></body></html>
"""

SAMPLE_RSS = """<?xml version="1.0"?>
<rss><channel>
<item>
  <title>Inquiry report</title>
  <link>https://example.com/report</link>
  <description>Government schedule pressure led to safety override and expert dissent
  was suppressed during the regulatory review process in 2024 according to witnesses.
  Parliamentary investigators documented bureaucratic opacity and inter-agency conflict
  across multiple oversight bodies during the public inquiry hearings.</description>
</item>
</channel></rss>"""


def test_html_to_text():
    text = html_to_text(SAMPLE_HTML)
    assert "Government management" in text
    assert "<p>" not in text


def test_normalize_hit_min_length():
    assert normalize_hit(source="t", source_type="t", title="x", text="short") is None
    hit = normalize_hit(
        source="t",
        source_type="t",
        title="x",
        text="x " * 120,
    )
    assert hit and hit["doc_id"].startswith("t-")


def test_fetch_url_mock():
    mock_resp = MagicMock()
    mock_resp.text = SAMPLE_HTML
    mock_resp.headers = {"content-type": "text/html"}
    mock_resp.raise_for_status = MagicMock()

    with patch("mas.ingest.fetchers.url.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.get.return_value = mock_resp
        hit = url.fetch_url("https://example.com/report")
    assert hit
    assert hit["title"] == "Test Report"
    assert len(hit["text"]) >= 200


def test_rss_parse_mock():
    mock_resp = MagicMock()
    mock_resp.content = SAMPLE_RSS.encode()
    mock_resp.raise_for_status = MagicMock()

    with patch("mas.ingest.fetchers.rss.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.get.return_value = mock_resp
        hits = rss.fetch_feed("https://example.com/feed.xml")
    assert len(hits) == 1
    assert hits[0]["title"] == "Inquiry report"


def test_rss_follow_link_when_summary_short():
    short_rss = """<?xml version="1.0"?>
<rss><channel>
<item>
  <title>Short BBC item</title>
  <link>https://example.com/full-article</link>
  <description>Brief politics summary.</description>
</item>
</channel></rss>"""
    mock_resp = MagicMock()
    mock_resp.content = short_rss.encode()
    mock_resp.raise_for_status = MagicMock()
    page_hit = {
        "doc_id": "url-x",
        "source": "url",
        "source_type": "web_page",
        "url": "https://example.com/full-article",
        "title": "Full Article",
        "country": "",
        "text": "Government management overruled engineers on safety " * 12,
    }

    with patch("mas.ingest.fetchers.rss.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.get.return_value = mock_resp
        with patch("mas.ingest.fetchers.rss.url_fetcher.fetch_url", return_value=page_hit) as fetch_url:
            hits = rss.fetch_feed("https://example.com/feed.xml")

    fetch_url.assert_called_once_with("https://example.com/full-article")
    assert len(hits) == 1
    assert len(hits[0]["text"]) >= 200


def test_ingest_batch(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "batch.db")
    init_db()

    result = ingest_batch([
        {
            "source": "exa_mcp",
            "source_type": "mcp_bridge",
            "title": "MCP article",
            "url": "https://example.com/a",
            "text": "NASA management overruled engineers on launch under schedule pressure. " * 5,
            "country": "USA",
        }
    ], auto_analyze=False)

    assert result["ingested"] == 1
    docs = list_raw_documents()
    assert docs[0]["source"] == "exa_mcp"


def test_ingest_url_mock(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "url.db")
    init_db()

    hit = {
        "doc_id": "url-test",
        "source": "url",
        "source_type": "web_page",
        "url": "https://example.com/r",
        "title": "Report",
        "country": "USA",
        "text": "Government schedule pressure safety override " * 12,
    }
    with patch("mas.ingest.service.url_fetcher.fetch_url", return_value=hit):
        with patch("mas.ingest.service._analyze_document") as analyze:
            analyze.return_value = {"case_id": "C-1", "cep": 0.3, "cat": "CAT-000"}
            result = ingest_url("https://example.com/r", auto_analyze=True)

    assert result["ok"]
    assert result["case_id"] == "C-1"


def test_run_rss_fetch_mock(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "rss.db")
    init_db()

    hits = [{
        "doc_id": "rss-1",
        "source": "rss",
        "source_type": "rss_feed",
        "url": "https://example.com/1",
        "title": "Feed item",
        "country": "UK",
        "text": "Parliamentary inquiry into regulatory failure " * 10,
    }]
    with patch("mas.ingest.service.rss_fetcher.fetch_feed", return_value=hits):
        with patch("mas.ingest.service._analyze_document") as analyze:
            analyze.return_value = {"case_id": "C-2", "cep": 0.2, "cat": "CAT-000"}
            result = run_rss_fetch(
                feeds=[{"url": "https://example.com/feed", "country": "UK"}],
                auto_analyze=True,
            )

    assert result["ok"]
    assert result["ingested"] == 1


def test_fetcher_status_has_keys():
    status = fetcher_status()
    for key in ("url", "rss", "openrouter", "gemini", "exa", "federal_register", "courtlistener", "oig"):
        assert key in status


def test_exa_search_mock(monkeypatch):
    monkeypatch.setenv("EXA_API_KEY", "test-key")
    from mas.ingest.fetchers import exa as exa_mod
    exa_mod._client.cache_clear()

    result = type("R", (), {
        "url": "https://example.com/gov-report",
        "title": "Oversight inquiry",
        "highlights": [
            "Government management overruled engineers on safety launch decision "
            "under intense schedule pressure from political leadership in 2024. "
            "Witnesses described regulatory capture and whistleblower suppression.",
        ],
    })()
    response = type("Resp", (), {"results": [result]})()

    with patch.object(exa_mod, "_client") as client_fn:
        client_fn.return_value.search.return_value = response
        with patch.object(exa_mod, "EXA_AGENT_MODE", False):
            hits = exa_mod.search("government regulatory failure report", num_results=3)

    assert len(hits) == 1
    assert hits[0]["source"] == "exa"
    assert hits[0]["url"] == "https://example.com/gov-report"
    assert len(hits[0]["text"]) >= 200


def test_exa_agent_search_mock(monkeypatch):
    monkeypatch.setenv("EXA_API_KEY", "test-key")
    from mas.ingest.fetchers import exa as exa_mod
    exa_mod._client.cache_clear()

    article_payload = {
        "articles": [{
            "title": "Parliamentary inquiry",
            "url": "https://example.com/inquiry",
            "excerpt": "Government schedule pressure led to safety override and expert dissent "
            "was suppressed during the regulatory review process in 2024 according to witnesses. "
            "Investigators documented bureaucratic opacity across agencies.",
            "country": "UK",
        }]
    }
    finished = type("Run", (), {
        "output": type("Out", (), {"structured": article_payload})(),
    })()

    with patch.object(exa_mod, "_client") as client_fn:
        agent = client_fn.return_value.agent
        agent.runs.create.return_value = type("Created", (), {"id": "run-1"})()
        agent.runs.poll_until_finished.return_value = finished
        hits = exa_mod.agent_search("UK regulatory failure inquiry", num_results=1)

    assert len(hits) == 1
    assert hits[0]["source"] == "exa_agent"
    assert hits[0]["country"] == "UK"
