# API reference

The public API consists of `gribify.grib2_message`, the identification and
product definition classes, and the parameter classes exposed through
`gribify.param_set`. Import parameter classes with
`from gribify import param_set`.

See [Examples](examples.md) for executable usage examples.
The reference below is generated from the Python sources and distributed
`.pyi` files. Constructor methods are shown explicitly so their typed arguments
remain visible. Each class also provides `__repr__` for its textual representation.

## Message generation

::: gribify.grib2_message
    options:
      heading_level: 3

## Identification

::: gribify.Identification
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

## Product definitions

::: gribify.ProductDefinition
    options:
      heading_level: 3
      members: [__new__, __repr__, template_num]
      show_if_no_docstring: true

::: gribify.Template4_0
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

::: gribify.Template4_1
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

::: gribify.Template4_8
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

## Common parameter groups

::: gribify.param_set.ProductParam
    options:
      heading_level: 3
      members: [__new__, __repr__, category, num]
      show_if_no_docstring: true

::: gribify.param_set.GeneratingProcess
    options:
      heading_level: 3
      members: [__new__, __repr__, process_type, background_process, process_id]
      show_if_no_docstring: true

::: gribify.param_set.ForecastTime
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

::: gribify.param_set.FixedSurface
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

::: gribify.param_set.Horizontal
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

## Ensemble and statistical parameter groups

::: gribify.param_set.EnsembleForecast
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

::: gribify.param_set.StatisticalProcess
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true

::: gribify.param_set.Statistical
    options:
      heading_level: 3
      members: [__new__, __repr__]
      show_if_no_docstring: true
