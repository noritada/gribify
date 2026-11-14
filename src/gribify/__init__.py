import numpy as np

from ._gribify import grib2_message as _grib2_message
from ._gribify import (
    param_set, Identification, ProductDefinition, Template4_0, Template4_1, Template4_8,
)
from typing import Literal, Union


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
    *,
    packing: Literal["complex", "simple"] = "complex",
    decimal_scale: int,
) -> bytes:
    """Encode a GRIB2 message.

    Parameters
    ----------
    discipline : int
        Discipline - GRIB Master Table Number (see Code Table 0.0).

        Encoded as an unsigned 8-bit integer. Accepted range: 0 to 255 (inclusive).
        Code-table validity is the caller's responsibility.
    ident : Identification
        Section 1 - Identification section.
    product : Union[ProductDefinition, bytes]
        Section 4 - Product definition section.

        Python wrapper: accepts a structured definition or raw section payload
        bytes, excluding the five-octet section header.
    lats : numpy.ndarray
        Python wrapper: nonempty one-dimensional float64 latitude array.
    lngs : numpy.ndarray
        Python wrapper: nonempty one-dimensional float64 longitude array.
    values : numpy.ndarray or numpy.ma.MaskedArray
        Grid values indexed by latitude, then longitude. Masked entries and
        NaNs are encoded as missing values.

        Requires a two-dimensional float64 array with shape
        ``(len(lats), len(lngs))``. Masked entries are filled with NaN,
        regardless of ``fill_value``, without modifying the input.
        Noncontiguous arrays and negative strides are supported.
        Dense arrays are encoded in memory order with matching grid scanning
        metadata; other layouts are copied in C order. Thus equivalent arrays
        can produce different bytes while preserving values at each coordinate.
    packing : {"complex", "simple"}, optional
        Python wrapper: selects complex packing (template 5.2, the default)
        or simple packing (template 5.0).

        Other strings raise ValueError.
    decimal_scale : int
        A strategy specifying how many decimal places to consider valid for the
        numbers. This strategy is effective for various types of data, such as
        observation data obtained from specific observation instruments, where
        precision is clearly defined.

        Encoded as a signed 16-bit sign-magnitude integer. Accepted range:
        -32767 to 32767 (inclusive). Python wrapper: passed to
        ``encoder::SimplePackingStrategy::Decimal`` for both packing methods;
        required, with no default. For example, 2 selects two decimal places, 0 selects
        units, and -1 selects tens. This controls the encoder's scaling,
        rather than applying Python's round function to the input. Actual
        precision also depends on the data range and binary packing scale.
        -32768 raises ValueError; values outside the signed 16-bit Python-to-Rust
        conversion range raise OverflowError. Non-integer values raise TypeError.

    Returns
    -------
    bytes
        The encoded GRIB2 message.
    """
    if np.ma.isMaskedArray(values):
        values = np.ascontiguousarray(values.filled(np.nan))
    return _grib2_message(
        discipline, ident, product, lats, lngs, values,
        packing=packing, decimal_scale=decimal_scale,
    )
