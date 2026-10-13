"""Regression tests for audit integrity, input constraints, and path handling."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.llm_factory import LLMFactory
from cli import _resolve_safe_path as main_safe_path
from graph_linker.cli import _resolve_safe_path as alternate_safe_path


def test_audit_chain_rejects_signature_tampering():
    trail = AuditTrail(secret_key="non-secret-test-key-123456")
    trail.log("tester", "unit", "EXECUTE", {"status": "OK"})
    trail.log("tester", "unit", "EXECUTE", {"status": "OK"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "FORGED"
    assert not trail.verify_integrity()


def test_audit_chain_rejects_hash_tampering_and_exposes_copies():
    trail = AuditTrail(secret_key="non-secret-test-key-123456")
    trail.log("tester", "unit", "EXECUTE", {"status": "OK"})
    trail.get_trail()[0]["event_type"] = "EXTERNAL"
    assert trail.verify_integrity()
    trail.logs[0]["payload_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_sensitive_attributes_are_rejected():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="safe", target_identifier="safe", primary_metric=1,
        attributes={"contact": "patient@example.com"},
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_metrics_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="t", target_identifier="k", primary_metric=value)
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="t", target_identifier="k", primary_metric=1, secondary_metric=value)


@pytest.mark.parametrize("checker", [main_safe_path, alternate_safe_path])
def test_sibling_directory_prefix_rejected(tmp_path, monkeypatch, checker):
    working = tmp_path / "work"
    sibling = tmp_path / "work-backup"
    working.mkdir()
    sibling.mkdir()
    monkeypatch.chdir(working)
    with pytest.raises(ValueError, match="outside the working directory"):
        checker(str(sibling / "secret.csv"))


def test_non_mock_providers_are_not_silently_mocked():
    with pytest.raises(ValueError, match="Only the deterministic mock"):
        LLMFactory.create("openai")


def test_api_audit_accepts_valid_payload_and_blocks_sensitive_metadata():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    ok = client.post("/api/audit", json={
        "task_id": "API-001", "target_identifier": "SPECIMEN-001",
        "primary_metric": 12.0, "attributes": {"method": "reference"},
    })
    assert ok.status_code == 200
    assert ok.json()["overall_urgency"] == "ROUTINE"

    unsafe = client.post("/api/audit", json={
        "task_id": "API-002", "target_identifier": "SPECIMEN-002",
        "primary_metric": 12.0, "attributes": {"email": "patient@example.com"},
    })
    assert unsafe.status_code == 422
    assert "patient@example.com" not in unsafe.text


def test_batch_output_path_symlinks_cannot_escape(tmp_path, monkeypatch):
    work = tmp_path / "work"
    outside = tmp_path / "outside"
    work.mkdir()
    outside.mkdir()
    (work / "alias").symlink_to(outside, target_is_directory=True)
    monkeypatch.chdir(work)
    with pytest.raises(ValueError, match="outside the working directory"):
        main_safe_path("alias/export.csv")
