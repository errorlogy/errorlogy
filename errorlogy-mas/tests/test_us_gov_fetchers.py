"""US government fetcher tests (no live network)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from mas.db import init_db, list_raw_documents
from mas.ingest import run_us_gov_fetch, us_gov_fetcher_status, fetcher_status
from mas.ingest.fetchers import (
    courtlistener,
    federal_register,
    govinfo,
    legiscan,
    oig,
)
from mas.ingest.fetchers._common import normalize_hit

_LONG_TEXT = (
    "Government management overruled engineers on safety launch decision "
    "under intense schedule pressure from political leadership in 2024. "
) * 8

_FR_RESPONSE = {
    "results": [
        {
            "title": "Agency Rule on Oversight",
            "html_url": "https://www.federalregister.gov/documents/2024/01/01/2024-00001",
            "publication_date": "2024-01-01",
            "agencies": [{"name": "Department of Example"}],
            "type": "Rule",
            "abstract": _LONG_TEXT,
            "document_number": "2024-00001",
        }
    ]
}

_CL_RESPONSE = {
    "results": [
        {
            "caseName": "United States v. Example Corp",
            "docket_absolute_url": "/docket/12345/united-states-v-example/",
            "court": "U.S. District Court",
            "cause": "Civil action regarding regulatory enforcement and oversight failure.",
            "suitNature": "Contract dispute with government procurement implications.",
            "docketNumber": "1:24-cv-001",
            "docket_id": 12345,
            "dateFiled": "2024-06-01",
        }
    ]
}

_GOVINFO_RESPONSE = {
    "results": [
        {
            "packageId": "GAO-24-100000",
            "title": "GAO Report on Agency Oversight",
            "dateIssued": "2024-05-01",
            "collectionCode": "GAOREPORTS",
            "governmentAuthor": ["Government Accountability Office"],
            "download": {"pdfLink": "https://www.govinfo.gov/link/pdf/GAO-24-100000"},
        }
    ]
}

_DOJ_OIG_HTML = f"""
<html><body>
<div class="views-row">
  <time datetime="2024-03-15T00:00:00Z"></time>
  <div class="views-field-title"><a href="/reports/2024/example">OIG Audit of Procurement</a></div>
  <span>Type:</span><span>Audit Report</span>
  <div class="views-field-field-doj-component"><div class="field-content">DOJ OIG</div></div>
</div>
</body></html>
<p>{_LONG_TEXT}</p>
"""

_LEGISCAN_MASTER = {
    "status": "OK",
    "masterlist": {"1": {"bill_id": 101}, "2": {"bill_id": 102}},
}

_LEGISCAN_BILL = {
    "status": "OK",
    "bill": {
        "bill_id": 101,
        "bill_number": "HR 100",
        "title": "Oversight Reform Act",
        "description": _LONG_TEXT,
        "url": "https://legiscan.com/US/bill/HR100/2024",
        "status_date": "2024-04-01",
        "body": "H",
    },
}


def test_normalize_hit_source_environment():
    hit = normalize_hit(
        source="federal_register",
        source_type="gov_api",
        title="Test",
        text=_LONG_TEXT,
        source_environment="legal_judicial",
        agency="DOJ",
    )
    assert hit
    assert hit["source_environment"] == "legal_judicial"
    assert hit["agency"] == "DOJ"


def test_federal_register_mock():
    mock_resp = MagicMock()
    mock_resp.json.return_value = _FR_RESPONSE
    mock_resp.raise_for_status = MagicMock()

    with patch("mas.ingest.fetchers.federal_register.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.get.return_value = mock_resp
        hits = federal_register.fetch_recent(limit=1)

    assert len(hits) == 1
    assert hits[0]["source"] == "federal_register"
    assert hits[0]["country"] == "USA"


def test_courtlistener_mock():
    mock_search = MagicMock()
    mock_search.json.return_value = _CL_RESPONSE
    mock_search.raise_for_status = MagicMock()

    with patch("mas.ingest.fetchers.courtlistener.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.get.return_value = mock_search
        hits = courtlistener.fetch_recent(limit=1)

    assert len(hits) == 1
    assert hits[0]["source"] == "courtlistener"
    assert "United States v. Example" in hits[0]["title"]


def test_govinfo_mock(monkeypatch):
    monkeypatch.setattr("mas.ingest.fetchers.govinfo.config.GOVINFO_API_KEY", "test-key")
    mock_post = MagicMock()
    mock_post.json.return_value = _GOVINFO_RESPONSE
    mock_post.raise_for_status = MagicMock()
    mock_get = MagicMock()
    mock_get.is_success = False

    with patch("mas.ingest.fetchers.govinfo.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.post.return_value = mock_post
        client.get.return_value = mock_get
        hits = govinfo.fetch_recent(limit=1)

    assert len(hits) == 1
    assert hits[0]["source"] == "govinfo"


def test_govinfo_not_configured_without_key(monkeypatch):
    monkeypatch.setattr("mas.ingest.fetchers.govinfo.config.GOVINFO_API_KEY", "")
    assert not govinfo.is_configured()
    assert govinfo.fetch_recent(limit=1) == []


def test_oig_mock():
    mock_resp = MagicMock()
    mock_resp.text = _DOJ_OIG_HTML
    mock_resp.raise_for_status = MagicMock()
    mock_resp.is_success = True

    with patch("mas.ingest.fetchers.oig.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.get.return_value = mock_resp
        hits = oig.fetch_recent(limit=1, office="doj")

    assert len(hits) == 1
    assert hits[0]["source"] == "oig"
    assert "OIG Audit" in hits[0]["title"]


def test_legiscan_mock(monkeypatch):
    monkeypatch.setattr("mas.ingest.fetchers.legiscan.config.LEGISCAN_API_KEY", "test-key")

    def fake_get(_client, api_key, **params):
        if params.get("op") == "getMasterList":
            return _LEGISCAN_MASTER
        if params.get("op") == "getBill":
            return _LEGISCAN_BILL
        return {"status": "ERROR"}

    with patch("mas.ingest.fetchers.legiscan._api_get", side_effect=fake_get):
        with patch("mas.ingest.fetchers.legiscan.httpx.Client"):
            hits = legiscan.fetch_recent(limit=1)

    assert len(hits) == 1
    assert hits[0]["source"] == "legiscan"


def test_us_gov_fetcher_status_keys():
    status = us_gov_fetcher_status()
    assert "federal_register" in status
    assert "courtlistener_recap" in status
    assert status["federal_register"] is True


def test_fetcher_status_includes_us_gov():
    status = fetcher_status()
    assert "federal_register" in status
    assert "courtlistener" in status
    assert "oig" in status


def test_run_us_gov_fetch_mock(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "usgov.db")
    init_db()

    hits = [{
        "doc_id": "fr-test",
        "source": "federal_register",
        "source_type": "gov_api",
        "url": "https://www.federalregister.gov/documents/2024/01/01/2024-00001",
        "title": "Agency Rule",
        "country": "USA",
        "text": _LONG_TEXT,
        "source_environment": "legal_judicial",
    }]

    with patch("mas.ingest.service.federal_register_fetcher.fetch_recent", return_value=hits):
        with patch("mas.ingest.service.courtlistener_fetcher.fetch_recent", return_value=[]):
            with patch("mas.ingest.service.oig_fetcher.fetch_recent", return_value=[]):
                with patch("mas.ingest.service._analyze_document") as analyze:
                    analyze.return_value = {"case_id": "C-US", "cep": 0.3, "cat": "CAT-000"}
                    result = run_us_gov_fetch(limit_per_source=1, auto_analyze=True)

    assert result["ok"]
    assert result["ingested"] >= 1
    docs = list_raw_documents()
    assert any(d["source"] == "federal_register" for d in docs)
