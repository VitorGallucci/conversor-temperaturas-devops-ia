"""Falha didática intencional; não pertence à suíte padrão em tests/."""

from conversor.core import convert


def test_intentional_wrong_expectation():
    assert convert(0, "C", "F") == 0, "Esperado errado de propósito: o correto é 32 °F"
