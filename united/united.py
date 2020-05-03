import copy
from dataclasses import dataclass

si_base_units = ["s", "kg", "A", "m", "K", "mol", "cd"]

S = "s"
KG = "kg"
A = "A"
M = "m"
K = "K"
MOL = "mol"
CD = "cd"


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
        # Extract list from lookup table which only contains entries which describe units by si-units
        si_conversions = [x for x in look_up_table
                          if set(x.numerators).issubset(si_base_units) and set(x.denominators).issubset(si_base_units)]
        for numerator in numerators:
            if numerator in si_base_units:
                self.numerators.append(numerator)
                continue
            for conversion in si_conversions:
                if conversion.result == numerator:
                    self.numerators += conversion.numerators
                    self.denominators += conversion.denominators
                    continue

        for denominator in denominators:
            if denominator in si_base_units:
                self.denominators.append(denominator)
                continue

            for conversion in si_conversions:
                if conversion.result == denominator:
                    self.numerators += conversion.denominators
                    self.denominators += conversion.numerators
                    continue
        tmp = copy.copy(self.numerators)
        for numerator in tmp:
            if numerator in self.denominators:
                self.denominators.remove(numerator)
                self.numerators.remove(numerator)

    def __mul__(self, other):
        result = Unit(copy.copy(self.numerators), copy.copy(self.denominators))
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
        return self * Unit(other.denominators, other.numerators)

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
        if string_numerators:
            string_numerators = string_numerators + "*" + numerator
        else:
            string_numerators = numerator

    for denominator in denominators:
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


@dataclass
class Conversion:
    """Class which stores information about a unit conversion"""
    numerators: tuple
    denominators: tuple
    result: str
    reciprocal: bool = True


look_up_table = [Conversion((M, M, KG), (S, S, S, A, A), "O"),
                 Conversion((M, M, KG), (S, S, S, A), "V"),
                 Conversion((S, S, S, S, A, A), (M, M, KG), "F"),
                 Conversion((S, S, S, A, A), (M, M, KG), "S"),
                 Conversion((M, M, KG), (S, S, S), "W"),
                 Conversion(("V",), (A,), "O"),
                 Conversion(("V", A), (), "W"),
                 Conversion((), ("O",), "S", False),
                 Conversion((A, S), (), "C")]
