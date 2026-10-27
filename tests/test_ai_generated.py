"""Casos propostos por API de IA; validar antes do merge."""

import pytest

from conversor.core import convert


@pytest.mark.parametrize(
    "value,source,target,expected",
    [
        (25, "C", "F", 77.0),
        (98.6, "F", "C", 37.0),
        (-10, "C", "F", 14.0),
        (50, "F", "C", 10.0),
        (0, "F", "C", -17.77777777777778),
    ],
)
def test_ai_regression(value, source, target, expected):
    assert convert(value, source, target) == pytest.approx(expected)
