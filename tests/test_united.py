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
    h = e * 1
    assert Counter(h.numerators) == Counter([ud.m, ud.m, ud.kg])
    assert Counter(h.denominators) == Counter([ud.s, ud.s, ud.s, ud.A])
    i = e * 1
    assert Counter(i.numerators) == Counter([ud.m, ud.m, ud.kg])
    assert Counter(i.denominators) == Counter([ud.s, ud.s, ud.s, ud.A])


def test_dividing():
    a = ud.Unit(["s"])
    b = a / a
    assert b.numerators == []
    assert b.denominators == []
    c = ud.Unit(["V"])
    d = c / a
    assert Counter(d.numerators) == Counter([ud.m, ud.m, ud.kg])
    assert Counter(d.denominators) == Counter([ud.s, ud.s, ud.s, ud.s, ud.A])
    e = a / 1
    assert e.numerators == [ud.s]
    assert e.denominators == []
    f = 1 / a
    assert f.numerators == []
    assert f.denominators == [ud.s]
    g = 1 // c
    assert Counter(g.numerators) == Counter([ud.s, ud.s, ud.s, ud.A])
    assert Counter(g.denominators) == Counter([ud.m, ud.m, ud.kg])


def test_add():
    a = ud.Unit(["s"])
    b = ud.Unit(["s"])
    c = a + b
    assert Counter(c.numerators) == Counter([ud.s])
    assert c.denominators == []
    d = ud.Unit(["V", "s"], ["cd", "C"])
    e = ud.Unit(["s", "V"], ["C"])
    f = ud.Unit(["cd"])
    g = d + e / f
    assert Counter(g.numerators) == Counter([ud.m, ud.m, ud.kg])
    assert Counter(g.denominators) == Counter([ud.s, ud.s, ud.s, ud.A, ud.cd, ud.A])
    with pytest.raises(ValueError):
        h = a + f
    with pytest.raises(ValueError):
        i = e + d


def test_sub():
    a = ud.Unit(["s"])
    b = ud.Unit(["s"])
    c = a - b
    assert Counter(c.numerators) == Counter([ud.s])
    assert c.denominators == []
    d = ud.Unit(["V", "s"], ["cd", "C"])
    e = ud.Unit(["s", "V"], ["C"])
    f = ud.Unit(["cd"])
    g = d - e / f
    assert Counter(g.numerators) == Counter([ud.m, ud.m, ud.kg])
    assert Counter(g.denominators) == Counter([ud.s, ud.s, ud.s, ud.A, ud.cd, ud.A])
    with pytest.raises(ValueError):
        h = a - f
    with pytest.raises(ValueError):
        i = e - d


def test_pow():
    a = ud.Unit(["s"])
    b = a**0
    assert b == 1
    c = a**1
    assert c.numerators == [ud.s]
    d = a**3
    assert d.numerators == [ud.s, ud.s, ud.s]
    e = a**-2
    assert e.denominators == [ud.s, ud.s]
    assert e.numerators == []
    f = ud.Unit(["C"], ["m"])
    g = f**2
    assert Counter(g.numerators) == Counter([ud.A, ud.A, ud.s, ud.s])
    assert Counter(g.denominators) == Counter([ud.m, ud.m])


def test_eq():
    a = ud.Unit(["V"])
    assert a == a
    b = ud.Unit(["V"])
    assert a == b
    c = ud.Unit(["m", "m", "kg"])
    assert not a == c


@pytest.mark.parametrize("numerator, denominator, expected",
                         [(["s"], [], "s"), (["V", "A"], [], "W"), ([], ["V", "A"], "1/W"), (["V"], ["A"], "Ω"),
                          (["m", "m", "kg"], ["s", "s", "s", "A"], "V"),
                          ([], ["Ω"], "S"), ([], ["A", "s"], "1/C"), (["F"], ["C"], "1/V"),
                          (["V", "s"], [], "Wb"), (["m", "kg"], ["s", "s"], "N"), ((), ("m", "kg"), "1/(m*kg)"),
                          (("m", "kg"), ("s",), "(m*kg)/s"), (("m", "kg"), ("s", "cd"), "(m*kg)/(s*cd)")])
def test_repr(numerator, denominator, expected):
    ud.Unit.priority_configuration = "default"
    a = ud.Unit(numerator, denominator)
    assert repr(a) == expected


def test_quantity_property():
    a = ud.Unit(["V"])
    assert a.quantity == "Voltage"
    b = ud.Unit(["V"], ["A"])
    assert b.quantity == "Resistance"
    c = a*b
    assert c.quantity == "Unknown"


@pytest.mark.parametrize("numerator, denominator, expected",
                         [(["m", "m", "kg"], ["s", "s"], "J"), (["V"], [], "J/C")])
def test_mechanic_prio(numerator, denominator, expected):
    ud.Unit.priority_configuration = "mechanic"
    a = ud.Unit(numerator, denominator)
    assert repr(a) == expected
