from functools import partial
from typing import Annotated, Any

import numpy
from openff.units import Quantity
from pint import DimensionalityError
from pydantic import BeforeValidator

try:
    from openmm.unit import Quantity as OpenMMQuantity
except ImportError:
    OpenMMQuantity = Any  # type: ignore


def quack_into_unit(
    quantity: (
        list | numpy.ndarray | bytes | float | int | str | Quantity | OpenMMQuantity
    ),
    unit: str,
) -> Quantity:
    """
    Like to_quantity, but takes raw numbers and tacks on amu units.

    If input is Quantity, tries to convert to the desired unit.

    If input is a string, tries to initialize and then convert to the desired unit.

    If input is a list, float, or int, tries to initialize with the desired unit.

    """
    if "openmm" in quantity.__class__.__module__:
        from openff.units.openmm import from_openmm

        return from_openmm(quantity).to(unit)

    if isinstance(quantity, Quantity):

        try:
            return quantity.to(unit)
        except DimensionalityError as error:
            raise ValueError from error

    if isinstance(quantity, str):

        try:
            return Quantity(quantity).to(unit)
        except (DimensionalityError, TypeError) as error:
            # should catch other errors here, too, since a lot of stuff can error out
            # from being passed to the Quantity constructor
            raise ValueError from error

    if isinstance(quantity, list):
        # need to special case list[openmm.unit.Quantity] for a special
        # case with box vectors from OpenMM objects
        if {str(type(element).__module__) for element in quantity} == {
            "openmm.unit.quantity"
        }:
            from openff.units.openmm import from_openmm

            return from_openmm(quantity).to(unit)

    if isinstance(quantity, (list, numpy.ndarray, float, int)):

        try:
            return Quantity(quantity, unit)
        except (DimensionalityError, TypeError) as error:
            raise ValueError from error

    if isinstance(quantity, bytes):

        dt = numpy.dtype(int).newbyteorder("<")
        return Quantity(numpy.frombuffer(quantity, dtype=dt), unit)

    raise ValueError


def build_unit_type(unit: str) -> type[Quantity]:
    return Annotated[  # type: ignore[return-value]
        Quantity,
        BeforeValidator(partial(quack_into_unit, unit=unit)),
    ]


(
    OnlyAMUQuantity,
    OnlyDegreeQuantity,
    OnlyElementaryChargeQuantity,
) = (
    build_unit_type(unit)
    for unit in [
        "amu",
        "degree",
        "elementary_charge",
    ]
)
