"""Bayesian multisource fusion tests."""

from mas.engine import bayesian_fusion, wms
from mas.schemas.case import WeakSignal


def _signal(
    signal_type: str,
    *,
    strength: float = 0.7,
    reliability: float = 0.75,
    env: str = "agency",
) -> WeakSignal:
    return WeakSignal(
        signal_type=signal_type,
        description="test",
        source_environment=env,
        strength=strength,
        reliability=reliability,
        temporal_relevance=0.85,
    )


def test_two_independent_signals_boost_fused():
    s1 = _signal("WMS-001", env="agency")
    s2 = _signal("WMS-003", env="court")
    one = bayesian_fusion.fuse_signals([s1])
    two = bayesian_fusion.fuse_signals([s1, s2])
    assert two > one


def test_correlated_signals_less_boost():
    s1 = _signal("WMS-001", env="agency")
    s2 = _signal("WMS-001", env="agency")
    s3 = _signal("WMS-003", env="court")
    correlated = bayesian_fusion.fuse_signals([s1, s2])
    independent = bayesian_fusion.fuse_signals([s1, s3])
    assert independent > correlated


def test_wms_uses_fusion_with_two_signals():
    signals = [
        _signal("WMS-002", strength=0.8, reliability=0.8),
        _signal("WMS-005", strength=0.75, reliability=0.7, env="oig"),
    ]
    fused_msi = wms.compute_msi(signals)
    single_msi = wms.compute_msi([signals[0]])
    assert fused_msi > single_msi
    assert 0.0 <= fused_msi <= 1.0


def test_fuse_by_cluster():
    signals = [
        _signal("WMS-001", strength=0.6),
        _signal("WMS-001", strength=0.65),
        _signal("WMS-004", strength=0.7, env="media"),
    ]
    clusters = bayesian_fusion.fuse_by_cluster(signals)
    assert "WMS-001" in clusters
    assert "WMS-004" in clusters
    assert all(0.0 <= v <= 1.0 for v in clusters.values())


def test_empty_fusion():
    assert bayesian_fusion.fuse_signals([]) == 0.0
