"""Tests for `united` package."""
import pytest
from collections import Counter

import united.united as ud


def test_initializing():
    a = ud.Unit(["s"])
    assert a.numerators == [ud.s]
    assert a.denominators == []
    b = ud.Unit(["kg"], ["s"])
    assert b.numerators == [ud.kg]
    assert b.denominators == [ud.s]
    c = ud.Unit(["C"])
    assert Counter(c.numerators) == Counter([ud.A, ud.s])
    assert c.denominators == []
    d = ud.Unit(["V"])
    assert Counter(d.numerators) == Counter([ud.m, ud.kg, ud.m])
    assert Counter(d.denominators) == Counter([ud.s, ud.s, ud.s, ud.A])


def test_multiplying():
    a = ud.Unit(["s"])
    b = a * a
    assert Counter(b.numerators) == Counter([ud.s, ud.s])
    assert a.numerators == [ud.s]
    c = ud.Unit([], ["s"])
    d = a * c
    assert d.numerators == []
    assert d.denominators == []
    e = ud.Unit(["V"])
    f = ud.Unit(["F"])
    g = e * f
    assert Counter(g.numerators) == Counter([ud.s, ud.A])
    assert g.denominators == []


def test_dividing():
    a = ud.Unit(["s"])
    b = a / a
    assert b.numerators == []
    assert b.denominators == []
    c = ud.Unit(["V"])
    d = c / a
    assert Counter(d.numerators) == Counter([ud.m, ud.m, ud.kg])
    assert Counter(d.denominators) == Counter([ud.s, ud.s, ud.s, ud.s, ud.A])


@pytest.mark.parametrize("numerator, denominator, expected",
                         [(["s"], [], "s"), (["V", "A"], [], "W"), ([], ["V", "A"], "1/(W)"), (["V"], ["A"], "Ω"),
                          (["m", "m", "kg"], ["s", "s", "s", "A"], "V"),
                          ([], ["Ω"], "S"), ([], ["A", "s"], "1/(C)"), (["F"], ["C"], "1/(V)"),
                          (["V", "s"], [], "Wb"), (["m", "kg"], ["s", "s"], "N")])
def test_repr(numerator, denominator, expected):
    ud.priority_configuration = "default"
    a = ud.Unit(numerator, denominator)
    assert repr(a) == expected


def test_mechanic_prio():
