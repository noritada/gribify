from datetime import datetime

import numpy as np

from ._gribify import generate_grib2 as _generate_grib2


def generate_grib2(
    dt: datetime, product: bytes, lats: np.ndarray, lngs: np.ndarray, values: np.ndarray
) -> bytes:
    return _generate_grib2(dt, product, lats, lngs, values)
