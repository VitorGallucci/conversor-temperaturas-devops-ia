"""Executa comandos reais e preserva stdout, stderr e códigos de saída."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    folder = Path("evidencias/logs")
    folder.mkdir(parents=True, exist_ok=True)
    Path("tmp").mkdir(exist_ok=True)
    environment = os.environ.copy()
    environment["TEMP"] = environment["TMP"] = str(Path("tmp").resolve())
    environment["PYTHONIOENCODING"] = "utf-8"
    py = sys.executable
    commands = [
        ("linter", [py, "-m", "ruff", "check", "."], 0),
        ("format", [py, "-m", "ruff", "format", "--check", "."], 0),
        ("intentional_failure", [py, "-m", "pytest", "fixtures/demo_failure.py", "-v"], 1),
        (
            "low_coverage",
            [
                py,
                "-m",
                "pytest",
                "tests/test_core.py",
                "-k",
                "reference_values",
                "--cov=conversor",
                "--cov-branch",
                "--cov-report=json:build/coverage.json",
                "--junitxml=build/junit.xml",
            ],
            0,
        ),
        ("low_input", [py, "-m", "scripts.coverage_input"], 0),
        (
            "low_gate",
            [
                py,
                "-m",
                "scripts.gate",
                "tests",
                "build/tests-input.json",
                "--output",
                "evidencias/low-gate.json",
            ],
            1,
        ),
        (
            "full_tests",
            [
                py,
                "-m",
                "pytest",
                "--basetemp=tmp/evidence-tests",
                "--tb=short",
                "--cov=conversor",
                "--cov-branch",
                "--cov-report=term-missing",
                "--cov-report=json:build/coverage.json",
                "--cov-report=html:build/htmlcov",
                "--cov-fail-under=90",
                "--junitxml=build/junit.xml",
            ],
            0,
        ),
        ("high_input", [py, "-m", "scripts.coverage_input"], 0),
        (
            "high_gate",
            [
                py,
                "-m",
                "scripts.gate",
                "tests",
                "build/tests-input.json",
                "--output",
                "evidencias/high-gate.json",
            ],
            0,
        ),
        ("build", [py, "-m", "scripts.build"], 0),
    ]
    results = []
    for name, args, expected in commands:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
            check=False,
        )
        output = "$ " + " ".join(args) + "\n\n" + result.stdout + result.stderr
        output += f"\nExit code: {result.returncode}; expected: {expected}\n"
        (folder / f"{name}.txt").write_text(output, encoding="utf-8")
        results.append(
            {
                "command": name,
                "exit_code": result.returncode,
                "expected": expected,
                "ok": result.returncode == expected,
            }
        )
    report = {"executed_at": datetime.now(timezone.utc).isoformat(), "results": results}
    (folder / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all(item["ok"] for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
