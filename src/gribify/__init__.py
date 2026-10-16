import numpy as np

from ._gribify import grib2_message as _grib2_message
from ._gribify import (
    param_set, Identification, ProductDefinition, Template4_0, Template4_1, Template4_8,
)
from typing import Union


__all__ = [
    "grib2_message", "param_set", "Identification",
    "ProductDefinition", "Template4_0", "Template4_1", "Template4_8",
]

def grib2_message(
    discipline: int,
    ident: Identification,
    product: Union[ProductDefinition, bytes],
    lats: np.ndarray[tuple[int], np.dtype[np.float64]],
    lngs: np.ndarray[tuple[int], np.dtype[np.float64]],
    values: np.ndarray[tuple[int, int], np.dtype[np.float64]],
) -> bytes:
    return _grib2_message(discipline, ident, product, lats, lngs, values)
