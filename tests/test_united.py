"""Tests for `sipyunits` package."""
import pytest
from collections import Counter

import united.united
from united.united import Unit


def test_initializing():
    a = Unit(["s"])
    assert a.numerators == ["s"]
    assert a.denominators == []
    b = Unit(["kg"], ["s"])
    assert b.numerators == ["kg"]
    assert b.denominators == ["s"]
    c = Unit(["C"])
    assert Counter(c.numerators) == Counter(["A", "s"])
    assert c.denominators == []
    d = Unit(["V"])
    assert Counter(d.numerators) == Counter(["m", "kg", "m"])
    assert Counter(d.denominators) == Counter(["s", "s", "s", "A"])


def test_multiplying():
    a = Unit(["s"])
    b = a * a
    assert Counter(b.numerators) == Counter(["s", "s"])
    assert a.numerators == ["s"]
    c = Unit([], ["s"])
    d = a * c
    assert d.numerators == []
    assert d.denominators == []
    e = Unit(["V"])
    f = Unit(["F"])
    g = e * f
    assert Counter(g.numerators) == Counter(["s", "A"])
    assert g.denominators == []


def test_dividing():
    a = Unit(["s"])
    b = a / a
    assert b.numerators == []
    assert b.denominators == []
    c = Unit(["V"])
    d = c / a
    assert Counter(d.numerators) == Counter(["m", "m", "kg"])
    assert Counter(d.denominators) == Counter(["s", "s", "s", "s", "A"])


@pytest.mark.parametrize("numerator, denominator, expected",
                         [(["s"], [], "s"), (["V", "A"], [], "W"), ([], ["V", "A"], "1/(W)"), (["V"], ["A"], "O"),
                          (["m", "m", "kg"], ["s", "s", "s", "A"], "V"),
                          ([], ["O"], "S"), ([], ["A", "s"], "1/(C)"), (["F"], ["C"], "1/(V)"),
                          (["V", "s"], [], "Wb"), (["m", "kg"], ["s", "s"], "N")])
def test_repr(numerator, denominator, expected):
    united.united.priority_configuration = "electric"
    a = Unit(numerator, denominator)
    assert repr(a) == expected
