"""Converte relatórios reais do pytest para a entrada do gate."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

coverage = json.loads(Path("build/coverage.json").read_text())
suite = ET.parse("build/junit.xml").getroot()
failed = sum(int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in suite.iter("testsuite"))
Path("build/tests-input.json").write_text(
    json.dumps({"coverage": coverage["totals"]["percent_covered"], "failed": failed}),
    encoding="utf-8",
)
