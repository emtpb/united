import copy
from dataclasses import dataclass


class BaseUnit:
    def __init__(self, unit, symbol=None):
        self.unit = unit
        self.symbol = symbol

    def __repr__(self):
        return self.unit


s = BaseUnit("s", "Time")
kg = BaseUnit("kg", "Mass")
A = BaseUnit("A", "Ampere")
m = BaseUnit("m", "Length")
K = BaseUnit("K", "Temperature")
mol = BaseUnit("mol", "Amount of substance")
cd = BaseUnit("cd", "Luminous intensity")
O = BaseUnit("Ω", "Resistance")
V = BaseUnit("V", "Voltage")
F = BaseUnit("F", "Capacitance")
S = BaseUnit("S", "Conductance")
W = BaseUnit("W", "Power")
C = BaseUnit("C", "Electric charge")
H = BaseUnit("H", "Electrical inductance")
Wb = BaseUnit("Wb", "Magnetic flux")
J = BaseUnit("J", "Energy")
N = BaseUnit("N", "Force")
T = BaseUnit("T", "Magnetic Induction")
Pa = BaseUnit("Pa", "Pressure")


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
                 Conversion((m, m, kg), (s, s, A, A), H),
                 Conversion((m, m, kg), (s, s, s), W),
                 Conversion((m, m, kg), (s, s, A), Wb),
                 Conversion((m, m, kg), (s, s), J),
                 Conversion((m, kg), (s, s), N),
                 Conversion((kg,), (s, s, A), T),
                 Conversion((kg,), (m, s, s), Pa),
                 Conversion((V,), (A,), O),
                 Conversion((V, A), (), W),
                 Conversion((), (O,), S, False),
                 Conversion((N, m), (), J),
                 Conversion((A, s), (), C)]

si_base_conversions = [x for x in look_up_table
                       if set(x.numerators).issubset(si_base_units.values())
                       and set(x.denominators).issubset(si_base_units.values())]

default_priority = [x for x in range(len(look_up_table))]

electric_priority = [0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 15, 6, 8, 10, 13]

mechanic_priority = [7, 8, 10, 14, 0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 15]

priority_dict = {"default": default_priority, "electric": electric_priority, "mechanic": mechanic_priority}

priority_configuration = "default"


class Unit:
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
        self.repr = None
        # Split given numerators into their si-base-units if needed
        for numerator in numerators:
            if numerator in [repr(x) for x in si_base_units.values()]:
                self.numerators.append(si_base_units[numerator])
                continue
            for conversion in si_base_conversions:
                if repr(conversion.result) == numerator:
                    self.numerators += conversion.numerators
                    self.denominators += conversion.denominators
                    continue
        # Split given denominators into their si-base-units if needed
        for denominator in denominators:
            if denominator in [repr(x) for x in si_base_units.values()]:
                self.denominators.append(si_base_units[denominator])
                continue

            for conversion in si_base_conversions:
                if repr(conversion.result) == denominator:
                    self.numerators += conversion.denominators
                    self.denominators += conversion.numerators
                    continue
        tmp = copy.copy(self.numerators)
        # Reduce fraction
        for numerator in tmp:
            if numerator in self.denominators:
                self.denominators.remove(numerator)
                self.numerators.remove(numerator)
        tmp_numerators = copy.copy(self.numerators)
        tmp_denominators = copy.copy(self.denominators)
        self.repr = find_units(tmp_numerators, tmp_denominators)

    def __mul__(self, other):
        result = Unit([repr(x) for x in self.numerators], [repr(x) for x in self.denominators])
        # Add numerators of the other unit or reduce the fraction
        for numerator in other.numerators:
            if numerator in result.denominators:
                result.denominators.remove(numerator)
            else:
                result.numerators.append(numerator)
        # Add denominators of the other unit or reduce the fraction
        for denominator in other.denominators:
            if denominator in result.numerators:
                result.numerators.remove(denominator)
            else:
                result.denominators.append(denominator)
        return result

    def __floordiv__(self, other):
        return self * Unit([repr(x) for x in other.denominators], [repr(x) for x in other.numerators])

    def __truediv__(self, other):
        return self // other

    def __repr__(self):
        return self.repr


def find_units(numerators, denominators):
    """Iterates over the look_up_table and tries to find conversion for the units until no further
    conversion is possible and returns a string representation.

    Args:
        numerators (list): List of the given numerators as si-base-units.
        denominators (list): List of the given denominators as si-based-units.

    Returns:
        str: Representation of the unit.
    """
    string_numerators = ""
    string_denominators = ""
    new_look_up_table = [look_up_table[x] for x in priority_dict[priority_configuration]]
    found = True
    # Try to find conversion for the units
    while found:
        found = False
        for conversion in new_look_up_table:
            if all([True if numerators.count(j) >= conversion.numerators.count(j) else False for j in
                    conversion.numerators]) and \
                    all([True if denominators.count(j) >= conversion.denominators.count(j) else False for j in
                         conversion.denominators]):
                for j in conversion.numerators:
                    numerators.remove(j)
                for j in conversion.denominators:
                    denominators.remove(j)
                numerators.append(conversion.result)
                found = True
                break

            elif all([True if numerators.count(j) >= conversion.denominators.count(j) else False for j in
                      conversion.denominators]) and \
                    all([True if denominators.count(j) >= conversion.numerators.count(j) else False for j in
                         conversion.numerators]) and conversion.reciprocal is True:
                for j in conversion.numerators:
                    denominators.remove(j)
                for j in conversion.denominators:
                    numerators.remove(j)
                denominators.append(conversion.result)
                found = True
                break
    # Convert the separate lists of numerators and denominators into a single string
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
