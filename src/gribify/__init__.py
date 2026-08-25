import numpy as np

from ._gribify import generate_grib2 as _generate_grib2
from ._gribify import param_set, Identification


__all__ = [
    "generate_grib2", "param_set", "Identification",
]

def generate_grib2(
    ident: Identification,
    product: bytes,
    lats: np.ndarray[tuple[int], np.dtype[np.float64]],
    lngs: np.ndarray[tuple[int], np.dtype[np.float64]],
    values: np.ndarray[tuple[int, int], np.dtype[np.float64]],
) -> bytes:
    return _generate_grib2(ident, product, lats, lngs, values)
