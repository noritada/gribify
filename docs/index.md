# gribify

`gribify` is a simple Python module designed specifically to generate GRIB2 data
from NumPy arrays and structured product metadata. It uses the Rust `grib` crate
as the encoding backend.

- [Examples](examples.md): write temperature, ensemble-member, and accumulated precipitation fields.
- [API reference](api.md): reference generated from the Python sources and type stubs.

## Development

The following pages are intended for library developers. Library users do not
need to refer to it.

- [Building the library](development/building.md): how to set up the development environment and build gribify.
- [Building the docs](development/docs.md): how to reproduce this static HTML site locally.
