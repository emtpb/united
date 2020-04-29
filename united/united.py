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
    def __init__(self, numerators=[], denominators=[]):

        self.numerators = []
        self.denominators = []

        for numerator in numerators:
            if numerator in si_base_units:
                self.numerators.append(numerator)
                continue

            unit_index = [x[2] for x in look_up_table].index(numerator)
            self.numerators += list(look_up_table[unit_index][0])
            self.denominators += list(look_up_table[unit_index][1])

        for denominator in denominators:
            if denominator in si_base_units:
                self.denominators.append(denominator)
                continue
            unit_index = [x[2] for x in look_up_table].index(denominator)
            self.numerators += list(look_up_table[unit_index][1])
            self.denominators += list(look_up_table[unit_index][0])
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
                 ((M, M, KG), (S, S, S), "W"),
                 (("V",), (A,), "O"),
                 (("V", A), (), "W"),
                 ((A, S), (), "C")]
