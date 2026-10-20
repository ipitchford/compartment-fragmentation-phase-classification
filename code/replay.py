#!/usr/bin/env python3
"""Run all finite checks in ordinary and optimized modes, fail closed."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = {
    "drift": ROOT / "code" / "verify_drift.py",
    "retention": ROOT / "code" / "verify_retention.py",
}
CONTROLS = {
    "drift": ("jensen", "variance"),
    "retention": ("mixture-variance", "uniform-row"),
}


def run(args: list[str], expected_success: bool) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, text=True, capture_output=True)
    if (proc.returncode == 0) != expected_success:
        raise RuntimeError(
            f"unexpected exit {proc.returncode} for {' '.join(args)}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    if not expected_success and "VerificationError" not in proc.stderr:
        raise RuntimeError(
            f"expected a VerificationError for {' '.join(args)}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def normalized(path: Path) -> dict:
    value = json.loads(path.read_text())
    value.pop("python_optimization_flag", None)
    return value


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    summaries = {}
    with tempfile.TemporaryDirectory(prefix="compartment-replay-") as tmp:
        tmpdir = Path(tmp)
        for name, script in SCRIPTS.items():
            normal = tmpdir / f"{name}-normal.json"
            optimized = tmpdir / f"{name}-optimized.json"
            run([sys.executable, "-B", str(script), "--output", str(normal)], True)
            run([sys.executable, "-B", "-O", str(script), "--output", str(optimized)], True)
            normal_report = json.loads(normal.read_text())
            optimized_report = json.loads(optimized.read_text())
            if normal_report.get("python_optimization_flag") != 0:
                raise RuntimeError(f"{name}: ordinary child did not report optimization flag 0")
            if optimized_report.get("python_optimization_flag") != 1:
                raise RuntimeError(f"{name}: optimized child did not report optimization flag 1")
            if normalized(normal) != normalized(optimized):
                raise RuntimeError(f"{name}: ordinary and optimized semantic receipts differ")
            for control in CONTROLS[name]:
                run([sys.executable, "-B", str(script), "--negative-control", control], False)
                run([sys.executable, "-B", "-O", str(script), "--negative-control", control], False)
            report = normal_report
            output_name = "compartment_drift_checks.json" if name == "drift" else "random_retention_exact.json"
            (RESULTS / output_name).write_text(json.dumps(report, indent=2) + "\n")
            summaries[name] = {
                "ordinary_replay": "passed",
                "optimized_replay": "passed",
                "negative_controls": [f"{control}_failed_as_required" for control in CONTROLS[name]],
            }

    receipt = {
        "checks": summaries,
        "semantic_receipts_equal_ignoring_optimization_flag": True,
        "scope": "finite exact and floating-point checks; analytic stochastic proofs remain controlling",
    }
    (RESULTS / "replay_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
