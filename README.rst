******
United
******

United tries to represent SI-units as optimal as possible by resolving "smaller" units into "bigger" units
via a look up table and supports various arithmetic operations between unit objects.

Example:
    Creating a unit with Volt V as a numerator and Ampere A as denominator will result into the
    unit Ohm Ω. Same goes for creating two separate units Volt and Ampere and dividing Ampere from Volt.

Features
========

* Arithmetic operations:
    * Multiplying
    * Dividing
    * Adding
    * Subtracting
    * Raising power
* Different priorities for the look up table
    * Default
    * Electric
    * Mechanic
