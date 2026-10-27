import pytest

from scripts import gate


@pytest.mark.parametrize(
    "kind,good,bad",
    [
        ("tests", {"coverage": 95, "failed": 0}, {"coverage": 30, "failed": 1}),
        ("metrics", {"p95_ms": 20, "error_rate": 0}, {"p95_ms": 900, "error_rate": 4}),
        ("logs", {"entries": [{"level": "INFO"}]}, {"entries": [{"level": "CRITICAL"}]}),
        (
            "traces",
            {"spans": [{"status": "ok", "duration_ms": 2}]},
            {"spans": [{"status": "timeout", "duration_ms": 1000}]},
        ),
        ("security", {"entries": []}, {"entries": [{"level": "CRITICAL"}]}),
        (
            "costs",
            {"idle_instances": 0, "monthly_brl": 0},
            {"idle_instances": 2, "monthly_brl": 250},
        ),
    ],
)
def test_gate_both_decisions(kind, good, bad):
    assert gate.evaluate(kind, good)["approved"] is True
    assert gate.evaluate(kind, bad)["approved"] is False


def test_ai_cannot_override_mandatory_failure(monkeypatch):
    monkeypatch.setattr(gate, "ask_ai", lambda *_: {"approved": True})
    assert gate.evaluate("tests", {"coverage": 10, "failed": 0}, "real")["approved"] is False


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("GROQCLOUD_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ausente"):
        gate.ask_ai("tests", {}, [])
