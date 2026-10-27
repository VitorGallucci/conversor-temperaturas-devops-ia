"""IA sugere dados de casos; gerador controlado produz código de testes."""

import json
import math
import os
import urllib.request
from pathlib import Path


def main():
    key = os.environ["GROQCLOUD_API_KEY"]
    core = Path("conversor/core.py").read_text(encoding="utf-8")
    tests = Path("tests/test_core.py").read_text(encoding="utf-8")
    payload = {
        "model": os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b"),
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "Revise o código e os testes. Gere 5 novos casos válidos C/F diferentes dos "
                    "existentes. Responda JSON com cases: lista de objetos com value (número), "
                    "source (C/F), target (C/F), expected (número); "
                    "release_notes: string em português. "
                    "Use cálculos corretos e nunca temperaturas abaixo do zero absoluto."
                ),
            },
            {"role": "user", "content": json.dumps({"source": core, "tests": tests})},
        ],
    }
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "termo-devops/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        answer = json.loads(json.load(response)["choices"][0]["message"]["content"])
    cases = answer["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 20:
        raise ValueError("Quantidade de casos inválida")
    rows = []
    for case in cases:
        for field in ("value", "expected"):
            if type(case[field]) not in (float, int) or not math.isfinite(case[field]):
                raise ValueError("Caso não numérico")
        if case["source"] not in ("C", "F") or case["target"] not in ("C", "F"):
            raise ValueError("Unidade inválida")
        rows.append((case["value"], case["source"], case["target"], case["expected"]))
    content = (
        '"""Casos propostos por API de IA; validar antes do merge."""\n'
        "import pytest\nfrom conversor.core import convert\n\n"
        '@pytest.mark.parametrize("value,source,target,expected", ' + repr(rows) + ")\n"
        "def test_ai_regression(value, source, target, expected):\n"
        "    assert convert(value, source, target) == pytest.approx(expected)\n"
    )
    Path("tests/test_ai_generated.py").write_text(content, encoding="utf-8")
    Path("docs").mkdir(exist_ok=True)
    Path("docs/AI_RELEASE_NOTES.md").write_text(
        "# Revisão por IA\n\n" + str(answer["release_notes"]), encoding="utf-8"
    )
    Path("build").mkdir(exist_ok=True)
    Path("build/ai-review.json").write_text(
        json.dumps(answer, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
