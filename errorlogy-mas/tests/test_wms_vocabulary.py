"""Tests for WMS taxonomy vocabulary binding."""

from mas.engine import wms
from mas.engine.wms_vocabulary import (
    WMS_UNK,
    get_wms_signal_catalog,
    ingest_metadata_to_signals,
    merge_weak_signals,
    normalize_signal_type,
    normalize_source_environment,
    normalize_weak_signal,
)
from mas.schemas.case import GovernanceCase, WeakSignal


def test_normalize_legacy_signal_types():
    assert normalize_signal_type("expert_dissent_suppressed") == "WMS-003"
    assert normalize_signal_type("schedule_pressure") == "WMS-006"
    assert normalize_signal_type("bureaucratic_opacity") == "WMS-011"
    assert normalize_signal_type("whistleblower_ignored") == "WMS-013"


def test_normalize_wms_ids_passthrough():
    assert normalize_signal_type("WMS-001") == "WMS-001"
    assert normalize_signal_type("WMS-020") == "WMS-020"


def test_normalize_unknown_returns_unk():
    assert normalize_signal_type("") == WMS_UNK
    assert normalize_signal_type("totally_unknown_signal") == WMS_UNK


def test_normalize_source_environment():
    assert normalize_source_environment("audit_oversight") == "audit_oversight"
    assert normalize_source_environment("public_record") == "media_investigative"
    assert normalize_source_environment("contractor") == "procurement_contracts"


def test_get_wms_signal_catalog_contains_all_ids():
    catalog = get_wms_signal_catalog()
    for i in range(1, 21):
        assert f"WMS-{i:03d}" in catalog
    assert "source_environment" in catalog


def test_ingest_metadata_creates_stub_signal():
    signals = ingest_metadata_to_signals(
        {"source_environment": "audit_oversight", "title": "GAO report", "agency": "GAO"}
    )
    assert len(signals) == 1
    assert signals[0].signal_type == "WMS-004"
    assert signals[0].source_environment == "audit_oversight"
    assert "GAO" in signals[0].description


def test_merge_weak_signals_dedupes():
    scout = [
        WeakSignal(
            signal_type="WMS-003",
            description="dissent",
            source_environment="experts_science",
            strength=0.8,
            reliability=0.7,
            temporal_relevance=0.9,
        )
    ]
    ingest = ingest_metadata_to_signals({"source_environment": "experts_science", "title": "Expert memo"})
    merged = merge_weak_signals(scout, ingest)
    assert len(merged) == 1

    ingest2 = ingest_metadata_to_signals({"source_environment": "audit_oversight", "title": "Audit"})
    merged2 = merge_weak_signals(scout, ingest2)
    assert len(merged2) == 2


def test_wms_environment_diversity_boosts_msi():
    single_env = GovernanceCase(
        case_id="T-1",
        title="t",
        description="d",
        country="US",
        domain="gov",
        year=2020,
        source_text="text",
        weak_signals=[
            WeakSignal(
                signal_type="WMS-003",
                description="a",
                source_environment="experts_science",
                strength=0.8,
                reliability=0.7,
                temporal_relevance=0.9,
            ),
            WeakSignal(
                signal_type="WMS-006",
                description="b",
                source_environment="experts_science",
                strength=0.7,
                reliability=0.7,
                temporal_relevance=0.8,
            ),
        ],
    )
    multi_env = single_env.model_copy(
        update={
            "weak_signals": merge_weak_signals(
                single_env.weak_signals,
                ingest_metadata_to_signals({"source_environment": "audit_oversight", "title": "Audit"}),
            )
        }
    )
    msi_single = wms.detect(single_env).msi
    msi_multi = wms.detect(multi_env).msi
    assert msi_multi > msi_single


def test_normalize_weak_signal_legacy():
    raw = WeakSignal(
        signal_type="expert_dissent_suppressed",
        description="x",
        source_environment="public_record",
        strength=0.5,
        reliability=0.5,
        temporal_relevance=0.5,
    )
    norm = normalize_weak_signal(raw)
    assert norm.signal_type == "WMS-003"
    assert norm.source_environment == "media_investigative"
