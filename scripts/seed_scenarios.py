"""Gera fixtures didáticas identificadas, nunca apresentadas como telemetria real."""

import json
from pathlib import Path

SCENARIOS = {
    "healthy": {
        "tests": {"coverage": 95, "failed": 0},
        "logs": {"entries": [{"level": "INFO", "message": "Conversão concluída"}]},
        "metrics": {"requests": 100, "p95_ms": 20, "error_rate": 0},
        "traces": {"spans": [{"name": "convert", "status": "ok", "duration_ms": 2}]},
        "security": {"entries": []},
        "costs": {"monthly_brl": 0, "idle_instances": 0},
    },
    "incident": {
        "tests": {"coverage": 20, "failed": 1},
        "logs": {"entries": [{"level": "CRITICAL", "message": "Falha interna no conversor"}]},
        "metrics": {"requests": 100, "p95_ms": 3500, "error_rate": 18},
        "traces": {"spans": [{"name": "convert", "status": "timeout", "duration_ms": 4200}]},
        "security": {"entries": [{"level": "CRITICAL", "message": "Achado simulado de segurança"}]},
        "costs": {"monthly_brl": 250, "idle_instances": 5},
    },
}


if __name__ == "__main__":
    for scenario, kinds in SCENARIOS.items():
        folder = Path("fixtures") / scenario
        folder.mkdir(parents=True, exist_ok=True)
        for kind, data in kinds.items():
            data["provenance"] = "Cenário sintético didático; não é medição de produção"
            (folder / f"{kind}.json").write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
