*****
Usage
*****

To use United in a project::

   >>> from united import Unit
   >>> my_unit = Unit(numerators = ["V"], denominators = ["A"])
   >>> my_unit
   Ω
   >>> my_unit.quantity
   Resistance

The Unit class also supports arithmetic operations::

   >>> ampere = Unit(["A"])
   >>> ampere**2
   A*A
   >>> second = Unit(["s"])
   >>> second * ampere
   C
