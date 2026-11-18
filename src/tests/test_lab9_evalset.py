"""M0 command-line checks run before completing the M1 taxonomy."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.fixture
def evalset_cli(tmp_path):
    source = tmp_path / "data/public_claims.jsonl"
    source.parent.mkdir()
    claim = {"claim_id": "C-001", "matrix_id": "T01", "expected": {"refund_vnd": 35000}}
    source.write_text(json.dumps(claim) + "\n", encoding="utf-8")

    def run_evalset(*args):
        return subprocess.run(
            [sys.executable, "-m", "lab9.evalset", *args],
            cwd=tmp_path,
            env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])},
            capture_output=True,
            text=True,
        )

    return run_evalset


def test_build_writes_items_and_labels_without_checking_tags(tmp_path, evalset_cli):
    result = evalset_cli("--build")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "problem(s)" not in result.stdout
    item = json.loads((tmp_path / "data/eval/eval_set_v1.jsonl").read_text(encoding="utf-8"))
    labels = json.loads((tmp_path / "data/eval/labels_v1.json").read_text(encoding="utf-8"))
    assert item["claim_id"] == "C-001"
    assert "expected" not in item
    assert labels == {"C-001": {"refund_vnd": 35000}}


def test_explicit_check_runs_after_build(tmp_path, evalset_cli):
    result = evalset_cli("--build", "--check")
    item = json.loads((tmp_path / "data/eval/eval_set_v1.jsonl").read_text(encoding="utf-8"))
    expected_problems = int(not item["failure_modes"])
    assert result.returncode == expected_problems, result.stdout + result.stderr
    assert f"{expected_problems} problem(s)" in result.stdout


def test_check_rejects_missing_tags(tmp_path, evalset_cli):
    evalset_cli("--build")
    items_path = tmp_path / "data/eval/eval_set_v1.jsonl"
    item = json.loads(items_path.read_text(encoding="utf-8"))
    item["failure_modes"] = []
    items_path.write_text(json.dumps(item) + "\n", encoding="utf-8")

    result = evalset_cli("--check")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "failure_modes empty" in result.stdout


@pytest.mark.student
def test_fm03_c002_trace_regression():
    """M1: the faulty shape misuses a ticket fact; the fixed shape does not."""
    from lab9.trace_case import investigate

    broken = investigate("seeded_regression", "C-002", 11)
    fixed = investigate("fixed", "C-002", 11)
    broken_trial, fixed_trial = broken["trial"], fixed["trial"]

    assert broken_trial["lab8_pass"] is False
    assert broken_trial["result"]["status"] == "resolved"
    assert broken_trial["snapshot"]["refund_vnd"] == 20000
    assert any(event.get("kind") == "model_override" and
               event.get("payload", {}).get("delay_days") == 5
               for event in broken_trial["events"])

    assert fixed_trial["lab8_pass"] is True
    assert fixed_trial["result"]["status"] == "denied"
    assert fixed_trial["snapshot"]["refund_vnd"] == 0
    assert fixed_trial["snapshot"]["refund_count"] == 0
    assert not any(event.get("kind") == "model_override"
                   for event in fixed_trial["events"])
