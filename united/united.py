import copy
from dataclasses import dataclass


class BaseUnit:
    def __init__(self, unit, quantity, symbol=None):
        self.unit = unit
        self.quantity = quantity
        self.symbol = symbol

    def __repr__(self):
        return self.unit


s = BaseUnit("s", "Time", "T")
kg = BaseUnit("kg", "Mass", "m")
A = BaseUnit("A", "Ampere", "I")
m = BaseUnit("m", "Length", "l")
K = BaseUnit("K", "Temperature", None)
mol = BaseUnit("mol", "Amount of substance", "N")
cd = BaseUnit("cd", "luminous intensity", "J")
O = BaseUnit("O", "Resistance", "R")
V = BaseUnit("V", "Voltage", "U")
F = BaseUnit("F", "Capacitance", "C")
S = BaseUnit("S", "Conductance", None)
W = BaseUnit("W", "Power", "P")
C = BaseUnit("C", "Electric charge", "Q")

si_base_units = {"s": s, "kg": kg, "A": A, "m": m, "K": K, "mol": mol, "cd": cd}


@dataclass
class Conversion:
    """Class which stores information about a unit conversion"""
    numerators: tuple
    denominators: tuple
    result: str
    reciprocal: bool = True


look_up_table = [Conversion((m, m, kg), (s, s, s, A, A), O),
                 Conversion((m, m, kg), (s, s, s, A), V),
                 Conversion((s, s, s, s, A, A), (m, m, kg), F),
                 Conversion((s, s, s, A, A), (m, m, kg), S),
                 Conversion((m, m, kg), (s, s, s), W),
                 Conversion((V,), (A,), O),
                 Conversion((V, A), (), W),
                 Conversion((), (O,), S, False),
                 Conversion((A, s), (), C)]


class CustomUnit:
    """Represents a Unit by storing the numerator and the denominators of the unit as Si-units.
    Supports arithmetic operations like multiplying and dividing with other :class:`.Unit` instances. When representing
    the unit an algorithm tries to find the best fitting unit out of the Si-units via a lookup table."""
    def __init__(self, numerators=[], denominators=[]):
        """Initializes the Unit class.

        Args:
            numerators (list): List of units which should be numerators.
            denominators (list): List of units which should be denominators.
        """
        self.numerators = []
        self.denominators = []
        # Extract list from lookup table which only contains entries which describe units by si-units
        si_conversions = [x for x in look_up_table
                          if set(x.numerators).issubset(si_base_units.values())
                          and set(x.denominators).issubset(si_base_units.values())]
        for numerator in numerators:
            if numerator in [repr(x) for x in si_base_units.values()]:
                self.numerators.append(si_base_units[numerator])
                continue
            for conversion in si_conversions:
                if repr(conversion.result) == numerator:
                    self.numerators += conversion.numerators
                    self.denominators += conversion.denominators
                    continue

        for denominator in denominators:
            if denominator in [repr(x) for x in si_base_units.values()]:
                self.denominators.append(si_base_units[denominator])
                continue

            for conversion in si_conversions:
                if repr(conversion.result) == denominator:
                    self.numerators += conversion.denominators
                    self.denominators += conversion.numerators
                    continue
        tmp = copy.copy(self.numerators)
        for numerator in tmp:
            if numerator in self.denominators:
                self.denominators.remove(numerator)
                self.numerators.remove(numerator)

    def __mul__(self, other):
        result = CustomUnit([repr(x) for x in self.numerators], [repr(x) for x in self.denominators])
        for numerator in other.numerators:
            if numerator in result.denominators:
                result.denominators.remove(numerator)
            else:
                result.numerators.append(numerator)
        for denominator in other.denominators:
            if denominator in result.numerators:
                result.numerators.remove(denominator)
            else:
                result.denominators.append(denominator)
        return result

    def __floordiv__(self, other):
        return self * CustomUnit([repr(x) for x in other.denominators], [repr(x) for x in other.numerators])

    def __truediv__(self, other):
        return self // other

    def __repr__(self):
        tmp_numerators = copy.copy(self.numerators)
        tmp_denominators = copy.copy(self.denominators)
        result_numerators = ""
        result_denominators = ""
        return find_units(result_numerators, result_denominators, tmp_numerators, tmp_denominators)


def find_units(string_numerators, string_denominators, numerators, denominators):
    found = True
    while found:
        found = False
        for conversion in look_up_table:
            if all([True if numerators.count(j) >= conversion.numerators.count(j) else False for j in conversion.numerators]) and \
                    all([True if denominators.count(j) >= conversion.denominators.count(j) else False for j in conversion.denominators]):
                for j in conversion.numerators:
                    numerators.remove(j)
                for j in conversion.denominators:
                    denominators.remove(j)
                numerators.append(conversion.result)
                found = True
                break

            elif all([True if numerators.count(j) >= conversion.denominators.count(j) else False for j in conversion.denominators]) and \
                    all([True if denominators.count(j) >= conversion.numerators.count(j) else False for j in conversion.numerators]) and conversion.reciprocal is True:
                for j in conversion.numerators:
                    denominators.remove(j)
                for j in conversion.denominators:
                    numerators.remove(j)
                denominators.append(conversion.result)
                found = True
                break

    for numerator in numerators:
        numerator = repr(numerator)
        if string_numerators:
            string_numerators = string_numerators + "*" + numerator
        else:
            string_numerators = numerator

    for denominator in denominators:
        denominator = repr(denominator)
        if string_denominators:
            string_denominators = string_denominators + "*" + denominator
        else:
            string_denominators = denominator

    if string_numerators and not string_denominators:
        return string_numerators
    elif string_denominators and not string_numerators:
        return "1/(" + string_denominators + ")"
    else:
        return "(" + string_numerators + ")/(" + string_denominators + ")"
