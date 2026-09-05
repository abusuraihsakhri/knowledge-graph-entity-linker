"""
Automated Pytest for knowledge-graph-entity-linker Enrichment Modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from enrichment import (
    EntityLinkingConfidenceScoringEngine,
    EntityDeduplicationEngine,
    EntityHistoryTrackingEngine,
    GraphExportFormatsEngine,
    GraphStatisticsDashboardEngine,
    KnowledgegraphentitylinkerEnrichmentSuite,
    enrichment_suite,
)

def test_enrichment_suite_execution():
    suite = KnowledgegraphentitylinkerEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) >= 1
    for k, v in res.items():
        assert v.status in ["OPTIMAL", "WARNING", "CRITICAL_ALERT"]
        assert isinstance(v.recommendations, list)

def test_enrichment_threshold_escalation():
    suite = KnowledgegraphentitylinkerEnrichmentSuite()
    res = suite.execute_all(primary_val=10.0, secondary_val=5.0)
    for k, v in res.items():
        assert v.status in ["WARNING", "CRITICAL_ALERT"]
        assert len(v.alerts) > 0


def test_enrichment_invalid_threshold_rejected():
    """Engines must reject non-positive thresholds."""
    import pytest
    with pytest.raises(ValueError):
        EntityLinkingConfidenceScoringEngine(threshold=-1.0)
    with pytest.raises(ValueError):
        EntityLinkingConfidenceScoringEngine(threshold=0)


def test_enrichment_engine_history_tracked():
    """Engeach engine records evaluation history."""
    engine = EntityLinkingConfidenceScoringEngine(threshold=1.0)
    assert len(engine.history) == 0
    engine.evaluate(0.5)
    engine.evaluate(1.5)
    assert len(engine.history) == 2
    assert engine.history[0].status == "OPTIMAL"
    assert engine.history[1].status == "WARNING"


def test_enrichment_suite_returns_all_features():
    """execute_all returns all five enrichment features."""
    suite = KnowledgegraphentitylinkerEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    expected_keys = {
        "EntityLinkingConfidenceScoringEngine",
        "EntityDeduplicationEngine",
        "EntityHistoryTrackingEngine",
        "GraphExportFormatsEngine",
        "GraphStatisticsDashboardEngine",
    }
    assert set(res.keys()) == expected_keys
