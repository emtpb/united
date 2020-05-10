"""Tests for `sipyunits` package."""
import pytest
from collections import Counter
import united.united as ud


def test_initializing():
    a = ud.CustomUnit(["s"])
    assert a.numerators == [ud.s]
    assert a.denominators == []
    b = ud.CustomUnit(["kg"], ["s"])
    assert b.numerators == [ud.kg]
    assert b.denominators == [ud.s]
    c = ud.CustomUnit(["C"])
    assert Counter(c.numerators) == Counter([ud.A, ud.s])
    assert c.denominators == []
    d = ud.CustomUnit(["V"])
    assert Counter(d.numerators) == Counter([ud.m, ud.kg, ud.m])
    assert Counter(d.denominators) == Counter([ud.s, ud.s, ud.s, ud.A])


def test_multiplying():
    a = ud.CustomUnit(["s"])
    b = a * a
    assert Counter(b.numerators) == Counter([ud.s, ud.s])
    assert a.numerators == [ud.s]
    c = ud.CustomUnit([], ["s"])
    d = a * c
    assert d.numerators == []
    assert d.denominators == []
    e = ud.CustomUnit(["V"])
    f = ud.CustomUnit(["F"])
    g = e * f
    assert Counter(g.numerators) == Counter([ud.s, ud.A])
    assert g.denominators == []


def test_dividing():
    a = ud.CustomUnit(["s"])
    b = a / a
    assert b.numerators == []
    assert b.denominators == []
    c = ud.CustomUnit(["V"])
    d = c / a
    assert Counter(d.numerators) == Counter([ud.m, ud.m, ud.kg])
    assert Counter(d.denominators) == Counter([ud.s, ud.s, ud.s, ud.s, ud.A])


@pytest.mark.parametrize("numerator, denominator, expected",
                         [(["s"], [], "s"), (["V", "A"], [], "W"), ([], ["V", "A"], "1/(W)"), (["V"], ["A"], "O"),
                          (["m", "m", "kg"], ["s", "s", "s", "A"], "V"),
                          ([], ["O"], "S"), ([], ["A", "s"], "1/(C)"), (["F"], ["C"], "1/(V)"),
                          (["V", "s"], [], "(m*m*kg)/(s*C)")])
def test_repr(numerator, denominator, expected):
    a = ud.CustomUnit(numerator, denominator)
    assert repr(a) == expected
