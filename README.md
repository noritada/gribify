# gribify -- GRIB generation in Python

`gribify` is a simple Python module designed specifically to generate GRIB2 data
from NumPy arrays and structured product metadata. It uses the Rust `grib` crate
as the encoding backend.

GRIB2, a format for grid-based meteorological data, contains a great deal of
metadata in addition to the grid values themselves. Examples include the grid
system defining the latitude and longitude coordinates of each point,
meteorological elements, and the data timestamp. The data timestamp must also
include information on both the reference time and the forecast time (e.g. "a
6-hour forecast generated at 6:00 UTC on January 1, 2026").

There are also several methods for compressing the data.

`gribify` aims to be a simple module specialized in allowing users to configure
these settings in detail to generate data in the GRIB format.


