import math

import pytest

from conversor.core import convert


@pytest.mark.parametrize(
    "value,source,target,expected",
    [
        (0, "C", "F", 32),
        (100, "C", "F", 212),
        (-40, "C", "F", -40),
        (32, "F", "C", 0),
        (212, "F", "C", 100),
        (-40, "F", "C", -40),
        (-273.15, "C", "F", -459.67),
        (-459.67, "F", "C", -273.15),
        (36.5, "C", "F", 97.7),
        (18, "C", "C", 18),
        (77, "F", "F", 77),
    ],
)
def test_reference_values(value, source, target, expected):
    assert convert(value, source, target) == pytest.approx(expected)


@pytest.mark.parametrize(
    "value,source,target",
    [
        (None, "C", "F"),
        (True, "C", "F"),
        ("25", "C", "F"),
        (math.nan, "C", "F"),
        (math.inf, "F", "C"),
        (-math.inf, "C", "F"),
        (-274, "C", "F"),
        (-460, "F", "C"),
        (25, "K", "C"),
        (25, "C", "K"),
        (10**400, "C", "F"),
        (1.7e308, "C", "F"),
    ],
)
def test_invalid_values(value, source, target):
    with pytest.raises(ValueError):
        convert(value, source, target)


@pytest.mark.parametrize("value", [-273.15, -250, -40, 0, 1.5, 37, 100, 10000])
def test_round_trip(value):
    assert convert(convert(value, "C", "F"), "F", "C") == pytest.approx(value)
