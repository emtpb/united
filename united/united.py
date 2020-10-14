import copy
from dataclasses import dataclass
from collections import Counter

"""Module for converting SI units automatically.

Attributes:
    si_base_units (dict): Convert SI base unit string into the corresponding
                          :class:`.NamedUnit`.
    conversion_list: Holds all possible :class:`.Conversions` for SI units.
    si_base_conversions (list): Extracted list from conversions_list which
                                only holds conversion from SI base units to
                                SI units.
    default_priority (list): Contains the indexes for how the conversion_list
                             should be sorted in default.
    electrical_priority (list): Contains the indexes for how the 
                                conversion_list should be sorted to prioritize 
                                electrical units. 
    mechanical_priority (list): Contains the indexes for how the 
                                conversion_list should be sorted to prioritize 
                                mechanical units.
    priority_dict: Maps strings to the according priority list.                   
"""


class NamedUnit:
    """Class storing known SI units with their unit symbol and the quantity
    name.
    """
    def __init__(self, unit, quantity):
        self.unit = unit
        self.quantity = quantity

    def __repr__(self):
        return self.unit


s = NamedUnit("s", "Time")
kg = NamedUnit("kg", "Mass")
A = NamedUnit("A", "Current")
m = NamedUnit("m", "Length")
K = NamedUnit("K", "Temperature")
mol = NamedUnit("mol", "Amount of substance")
cd = NamedUnit("cd", "Luminous intensity")
Ohm = NamedUnit("Ω", "Resistance")
V = NamedUnit("V", "Voltage")
F = NamedUnit("F", "Capacitance")
S = NamedUnit("S", "Conductance")
W = NamedUnit("W", "Power")
C = NamedUnit("C", "Electric charge")
H = NamedUnit("H", "Inductance")
Wb = NamedUnit("Wb", "Magnetic flux")
J = NamedUnit("J", "Energy")
N = NamedUnit("N", "Force")
T = NamedUnit("T", "Magnetic Induction")
Pa = NamedUnit("Pa", "Pressure")
Hz = NamedUnit("Hz", "Frequency")

si_base_units = {"s": s, "kg": kg, "A": A, "m": m, "K": K, "mol": mol,
                 "cd": cd}


@dataclass
class Conversion:
    """Class to store information about a unit conversion."""
    numerators: tuple
    denominators: tuple
    result: NamedUnit
    reciprocal: bool = True
    match_exactly: bool = False


conversion_list = [Conversion((m, m, kg), (s, s, s, A), V),
                   Conversion((m, m, kg), (s, s, s, A, A), Ohm),
                   Conversion((s, s, s, s, A, A), (m, m, kg), F),
                   Conversion((s, s, s, A, A), (m, m, kg), S),
                   Conversion((m, m, kg), (s, s, A, A), H),
                   Conversion((m, m, kg), (s, s, s), W),
                   Conversion((m, m, kg), (s, s, A), Wb),
                   Conversion((m, m, kg), (s, s), J),
                   Conversion((m, kg), (s, s), N),
                   Conversion((kg,), (s, s, A), T),
                   Conversion((kg,), (m, s, s), Pa),
                   Conversion((V,), (A,), Ohm),
                   Conversion((V, A), (), W),
                   Conversion((), (Ohm,), S, False),
                   Conversion((N, m), (), J),
                   Conversion((A, s), (), C),
                   Conversion((), (s,), Hz, False, True)
                   ]

si_base_conversions = [x for x in conversion_list
                       if set(x.numerators).issubset(si_base_units.values())
                       and set(x.denominators).issubset(si_base_units.values())]


default_priority = [x for x in range(len(conversion_list))]

electrical_priority = [0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 15, 6, 8, 10, 13]

mechanical_priority = [7, 8, 10, 14, 0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 15]

priority_dict = {"default": default_priority,
                 "electrical": electrical_priority,
                 "mechanical": mechanical_priority}


class Unit:
    """Represents a Unit by storing the numerator and the denominators of the
    unit as SI units. Supports arithmetic operations like multiplying and
    dividing with other :class:`.Unit` instances. When representing the unit,
    an algorithm tries to find the best fitting unit out of the SI units via
    a lookup table."""

    conversion_priority = "default"

    def __init__(self, numerators=None, denominators=None, fix_repr=False):
        """Initializes the Unit class.

        Args:
            numerators (list): List of units which should be numerators.
            denominators (list): List of units which should be denominators.
            fix_repr (bool): When set to True the repr of the unit will be the
                             exact same as given by parameters numerators and
                             denominators. This means there will be no
                             resolving of the unit via the conversion list.
        """
        if priority_dict.get(self.conversion_priority) is None:
            raise ValueError("Unknown priority '{}'".format(
                self.conversion_priority))
        if numerators is None:
            numerators = []

        if denominators is None:
            denominators = []

        self.numerators = []
        self.denominators = []
        self.repr = None
        # Split given numerators into their SI base units if needed
        for numerator in numerators:
            if numerator in [repr(x) for x in si_base_units.values()]:
                self.numerators.append(si_base_units[numerator])
                continue
            for conversion in si_base_conversions:
                if repr(conversion.result) == numerator:
                    self.numerators += conversion.numerators
                    self.denominators += conversion.denominators
                    continue
        # Split given denominators into their SI base units if needed
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

        if fix_repr is False:
            self.reduced_numerators = copy.copy(self.numerators)
            self.reduced_denominators = copy.copy(self.denominators)

            look_up_table = [conversion_list[x] for x in
                             priority_dict[Unit.conversion_priority]]
            found = True
            # Try to find conversion for the units
            while found:
                found = False
                for conversion in look_up_table:
                    if test_divider(conversion.numerators,
                                    conversion.denominators,
                                    self.reduced_numerators,
                                    self.reduced_denominators) \
                            and not conversion.match_exactly:
                        for j in conversion.numerators:
                            self.reduced_numerators.remove(j)
                        for j in conversion.denominators:
                            self.reduced_denominators.remove(j)
                        self.reduced_numerators.append(conversion.result)
                        found = True
                        break

                    elif test_divider(conversion.denominators,
                                      conversion.numerators,
                                      self.reduced_numerators,
                                      self.reduced_denominators) and \
                            conversion.reciprocal and \
                            not conversion.match_exactly:
                        for j in conversion.numerators:
                            self.reduced_denominators.remove(j)
                        for j in conversion.denominators:
                            self.reduced_numerators.remove(j)
                        self.reduced_denominators.append(conversion.result)
                        found = True
                        break
                    elif conversion.match_exactly and \
                            all([True if self.reduced_numerators.count(j) == conversion.numerators.count(j)
                                else False for j in self.reduced_numerators]) and \
                            all([True if self.reduced_denominators.count(j) == conversion.denominators.count(j)
                                else False for j in self.reduced_denominators]):
                        self.reduced_numerators = [conversion.result]
                        self.reduced_denominators = []
                        found = True
                        break
            self.repr = convert_fraction_to_string(self.reduced_numerators,
                                                   self.reduced_denominators)
        else:
            self.repr = convert_fraction_to_string(numerators, denominators)

    def __mul__(self, other):
        if isinstance(other, int):
            if other == 1:
                return copy.copy(self)
            else:
                raise TypeError("Unsupported operand for integer other than 1")
        result_numerators = copy.copy(self.numerators)
        result_denominators = copy.copy(self.denominators)
        # Add numerators of the other unit or reduce the fraction
        for numerator in other.numerators:
            if numerator in result_denominators:
                result_denominators.remove(numerator)
            else:
                result_numerators.append(numerator)
        # Add denominators of the other unit or reduce the fraction
        for denominator in other.denominators:
            if denominator in result_numerators:
                result_numerators.remove(denominator)
            else:
                result_denominators.append(denominator)
        return Unit([repr(x) for x in result_numerators],
                    [repr(x) for x in result_denominators])

    __rmul__ = __mul__

    def __floordiv__(self, other):
        if isinstance(other, int):
            if other == 1:
                return copy.copy(self)
            raise TypeError("Unsupported operand for integer other than 1")
        return self * Unit([repr(x) for x in other.denominators],
                           [repr(x) for x in other.numerators])

    def __rfloordiv__(self, other):
        if isinstance(other, int):
            if other == 1:
                return Unit([repr(x) for x in self.denominators],
                            [repr(x) for x in self.numerators])
            raise TypeError("Unsupported operand for integer other than 1")

    __truediv__ = __floordiv__
    __rtruediv__ = __rfloordiv__

    def __add__(self, other):
        if Counter(self.numerators) == Counter(other.numerators) and \
                Counter(self.denominators) == Counter(other.denominators):
            return copy.copy(self)
        else:
            raise ValueError("Cannot add unequal units")

    def __sub__(self, other):
        return self + other

    def __pow__(self, power, modulo=None):
        result = 1
        if power == 0:
            return result
        tmp = copy.copy(self)
        for i in range(abs(power)):
            result = result * tmp
        if power < 0:
            result = 1 / result
        return result

    def __eq__(self, other):
        if Counter(self.numerators) == Counter(other.numerators) \
                and Counter(self.denominators) == Counter(other.denominators):
            return True
        else:
            return False

    def __repr__(self):
        return self.repr

    @property
    def quantity(self):
        """Returns the quantity of the unit if it is a known SI unit."""
        if len(self.reduced_numerators) == 1 and not self.reduced_denominators:
            return self.reduced_numerators[0].quantity


def convert_fraction_to_string(numerators, denominators):
    """Converts numerators and denominators into a single fraction string.

    Args:
        numerators(list): List of units as the numerators. Can be unit objects
                          or strings.
        denominators(list): List of units as the denominators. Can be unit
                            objects or strings.
    """
    string_numerators = ""
    string_denominators = ""
    for numerator in numerators:
        if string_numerators:
            string_numerators = "{}*{}".format(string_numerators, numerator)
        else:
            string_numerators = "{}".format(numerator)

    for denominator in denominators:
        if string_denominators:
            string_denominators = "{}*{}".format(string_denominators,
                                                 denominator)
        else:
            string_denominators = "{}".format(denominator)
    if not string_numerators and not string_denominators:
        return "1"
    elif string_numerators and not string_denominators:
        return string_numerators
    elif string_denominators and not string_numerators:
        if "*" in string_denominators:
            return "1/(" + string_denominators + ")"
        else:
            return "1/" + string_denominators
    else:
        if "*" in string_numerators:
            string_numerators = "(" + string_numerators + ")"
        if "*" in string_denominators:
            string_denominators = "(" + string_denominators + ")"

        return string_numerators + "/" + string_denominators


def test_divider(numerators_first, denominators_first, numerators_second,
                 denominators_second):
    """Returns whether the first fraction divides the second fraction.

    Args:
        numerators_first (tuple): Numerators of the first fraction.
        denominators_first (tuple): Denominators of the first fraction.
        numerators_second (tuple): Numerators of the second fraction.
        denominators_second (tuple): Denominators of the second fraction.
    """
    if all([True if numerators_second.count(j) >= numerators_first.count(j)
            else False for j in numerators_first]) and \
        all([True if denominators_second.count(j) >= denominators_first.count(j)
            else False for j in denominators_first]):
        return True
    else:
        return False
