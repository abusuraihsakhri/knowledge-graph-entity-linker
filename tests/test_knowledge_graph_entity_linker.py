"""
Automated Pytest Test Suite for Knowledge Graph Entity Linker.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_requires_strong_key():
    """AuditTrail must reject weak or missing keys."""
    # Explicit short key is rejected
    with pytest.raises(SecurityException):
        AuditTrail(secret_key="short")
    # Valid explicit key works
    trail = AuditTrail(secret_key="a-strong-test-key-1234567890")
    assert trail.secret_key == b"a-strong-test-key-1234567890"


def test_audit_trail_with_env_key(monkeypatch):
    """AuditTrail picks up AUDIT_SECRET_KEY from environment."""
    monkeypatch.setenv("AUDIT_SECRET_KEY", "env-based-key-1234567890123456")
    trail = AuditTrail()
    assert trail.secret_key == b"env-based-key-1234567890123456"


def test_phi_guard_redaction():
    """PHIGuard.redact_phi masks SSNs and other identifiers."""
    text = "Patient MRN-123456 has SSN 123-45-6789"
    redacted = PHIGuard.redact_phi(text)
    assert "123-45-6789" not in redacted
    assert "REDACTED_IDENTIFIER" in redacted


def test_batch_path_traversal_rejected():
    """Batch command must reject paths outside working directory."""
    from cli import _resolve_safe_path
    with pytest.raises(ValueError, match="outside the working directory"):
        _resolve_safe_path("../../etc/passwd", must_exist=False)


def test_batch_missing_input_rejected():
    """Batch command must reject non-existent input files."""
    from cli import _resolve_safe_path
    with pytest.raises(FileNotFoundError):
        _resolve_safe_path("/nonexistent/file.csv", must_exist=True)
