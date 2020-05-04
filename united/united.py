import copy

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
        self.repr = None
        # Extract list from lookup table which only contains entries which describe units by si-units
        units_in_si = [x for x in look_up_table
                       if set(x[0]).issubset(si_base_units) and set(x[1]).issubset(si_base_units)]
        # Search si representation of all given numerators and add them to the numerator list
        for numerator in numerators:
            if numerator in si_base_units:
                self.numerators.append(numerator)
                continue
            for i in units_in_si:
                if i[2] == numerator:
                    self.numerators += i[0]
                    self.denominators += i[1]
                    continue
        # Search si representation of all given denominators and add them to the denominator list
        for denominator in denominators:
            if denominator in si_base_units:
                self.denominators.append(denominator)
                continue

            for i in units_in_si:
                if i[2] == denominator:
                    self.numerators += i[1]
                    self.denominators += i[0]
                    continue
        tmp = copy.copy(self.numerators)
        for numerator in tmp:
            if numerator in self.denominators:
                self.denominators.remove(numerator)
                self.numerators.remove(numerator)
        # Calculates the representation of the created unit
        tmp_numerators = copy.copy(self.numerators)
        tmp_denominators = copy.copy(self.denominators)
        result_numerators = ""
        result_denominators = ""
        self.repr = find_units(result_numerators, result_denominators, tmp_numerators, tmp_denominators)

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
        return self.repr


def find_units(string_numerators, string_denominators, numerators, denominators):
    changed = False
    found = True
    while found:
        found = False
        for i in look_up_table:
            if all([True if numerators.count(j) >= i[0].count(j) else False for j in i[0]]) and \
                    all([True if denominators.count(j) >= i[1].count(j) else False for j in i[1]]):

                for j in i[0]:
                    numerators.remove(j)
                for j in i[1]:
                    denominators.remove(j)
                numerators.append(i[2])
                found = True
                changed = True
                break

            elif all([True if numerators.count(j) >= i[1].count(j) else False for j in i[1]]) and \
                    all([True if denominators.count(j) >= i[0].count(j) else False for j in i[0]]):
                for j in i[0]:
                    denominators.remove(j)
                for j in i[1]:
                    numerators.remove(j)
                denominators.append(i[2])
                changed = True
                found = True
                break
    if changed:
        return find_units(string_numerators, string_denominators, numerators, denominators)
    else:
        for i in numerators:
            if string_numerators:
                string_numerators = string_numerators + "*" + i
            else:
                string_numerators = i

        for i in denominators:
            if string_denominators:
                string_denominators = string_denominators + "*" + i
            else:
                string_denominators = i

        if string_numerators and not string_denominators:
            return string_numerators
        elif string_denominators and not string_numerators:
            return "1/(" + string_denominators + ")"
        else:
            return "(" + string_numerators + ")/(" + string_denominators + ")"


look_up_table = [((M, M, KG), (S, S, S, A, A), "O"),
                 ((M, M, KG), (S, S, S, A), "V"),
                 ((S, S, S, S, A, A), (M, M, KG), "F"),
                 ((S, S, S, A, A), (M, M, KG), "S"),
                 ((M, M, KG), (S, S, A, A), "H"),
                 ((M, M, KG), (S, S, S), "W"),
                 ((M, M, KG), (S, S, A), "Wb"),
                 ((M, M, KG), (S, S), "J"),
                 ((M, KG), (S, S), "N"),
                 ((KG,), (S, S, A), "T"),
                 ((KG,), (M, S, S), "Pa"),
                 (("V",), (A,), "O"),
                 (("V", A), (), "W"),
                 (("N", M), (), "J"),
                 ((A, S), (), "C"),
                 ]
