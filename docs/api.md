# API reference

The public API consists of `gribify.grib2_message`, the identification and
product definition classes, and the parameter classes exposed through
`gribify.param_set`. Import parameter classes with
`from gribify import param_set`.

See [Examples](examples.md) for executable usage examples.
The reference below is generated from the Python sources and distributed
`.pyi` files. Constructor methods are shown explicitly so their typed arguments
remain visible. Each class also provides `__repr__` for its textual representation.

## Code Table 0.0 string values

`grib2_message(discipline=...)` accepts integer codes or these strings, based on
[ECMWF Code Table 0.0](https://codes.ecmwf.int/grib/format/grib2/ctables/0/0/).

<!-- codegen:discipline:start -->
| Code | Strings |
| --- | --- |
| 0 | `"meteorological"` |
| 1 | `"hydrological"` |
| 2 | `"land surface"` |
| 3 | `"satellite remote sensing"`, `"space"` |
| 4 | `"space weather"` |
| 10 | `"oceanographic"` |
| 20 | `"health and socioeconomic"` |
<!-- codegen:discipline:end -->

Strings are case-sensitive and must match exactly. The names omit `products`;
code 3 also accepts `"space"`, and code 20 uses `"health and socioeconomic"`.
For example, use `discipline="meteorological"` in place of `discipline=0`.
Missing has no string alias; integer `255` remains accepted. Integer codes retain
an unsigned 8-bit accepted range of 0 to 255 (inclusive), including reserved codes.
Unknown strings raise `ValueError`, out-of-range integers raise `OverflowError`,
and other types raise `TypeError`.

## Code Table 1.2 string values

`Identification(ref_time_significance=...)` accepts integer codes or these
strings from [ECMWF Code Table 1.2](https://codes.ecmwf.int/grib/format/grib2/ctables/1/2/),
with the first letter of each Meaning changed to lowercase.

<!-- codegen:ref_time_significance:start -->
| Code | Strings |
| --- | --- |
| 0 | `"analysis"` |
| 1 | `"start of forecast"` |
| 2 | `"verifying time of forecast"` |
| 3 | `"observation time"` |
| 4 | `"local time"` |
| 5 | `"simulation start"` |
<!-- codegen:ref_time_significance:end -->

Strings are case-sensitive and must match exactly. For example, use
`ref_time_significance="start of forecast"` in place of `ref_time_significance=1`.
Missing has no string alias; integer `255` remains accepted. Integer codes retain
an unsigned 8-bit accepted range of 0 to 255 (inclusive), including reserved codes.
Unknown strings raise `ValueError`, out-of-range integers raise `OverflowError`,
and other types raise `TypeError`.

## Code Table 1.4 string values

`Identification(data_type=...)` accepts integer codes or these strings, based on
[ECMWF Code Table 1.4](https://codes.ecmwf.int/grib/format/grib2/ctables/1/4/).
The strings use lowercase letters, omit a trailing `products`, and replace a
trailing `observations` with `observation`.

<!-- codegen:data_type:start -->
| Code | Strings |
| --- | --- |
| 0 | `"analysis"` |
| 1 | `"forecast"` |
| 2 | `"analysis and forecast"` |
| 3 | `"control forecast"` |
| 4 | `"perturbed forecast"` |
| 5 | `"control and perturbed forecast"` |
| 6 | `"processed satellite observation"` |
| 7 | `"processed radar observation"` |
| 8 | `"event probability"` |
| 9 | `"experimental data"` |
| 10 | `"ml based forecast"` |
<!-- codegen:data_type:end -->

Strings are case-sensitive and must match exactly. For example, use
`data_type="forecast"` in place of `data_type=1`.
Missing has no string alias; integer `255` remains accepted. Integer codes retain
an unsigned 8-bit accepted range of 0 to 255 (inclusive), including reserved codes.
Unknown strings raise `ValueError`, out-of-range integers raise `OverflowError`,
and other types raise `TypeError`.

## Code Table 4.4 string values

`ForecastTime(unit=...)` and `StatisticalProcess(time_range_unit=...,
time_increment_unit=...)` accept integers or the strings below, based on
[ECMWF Code Table 4.4](https://codes.ecmwf.int/grib/format/grib2/ctables/4/4/).

<!-- codegen:time_range_unit:start -->
| Code | Strings |
| --- | --- |
| 0 | `"minute"` |
| 1 | `"hour"` |
| 2 | `"day"` |
| 3 | `"month"` |
| 4 | `"year"` |
| 5 | `"decade"`, `"10 years"` |
| 6 | `"normal"`, `"30 years"` |
| 7 | `"century"`, `"100 years"` |
| 10 | `"3 hours"` |
| 11 | `"6 hours"` |
| 12 | `"12 hours"` |
| 13 | `"second"` |
<!-- codegen:time_range_unit:end -->

Strings are case-sensitive and must match exactly. For example,
`param_set.ForecastTime(0, 0, "minute", 30)` is equivalent to
`param_set.ForecastTime(0, 0, 0, 30)`. Unknown strings raise `ValueError`.
Missing has no string alias; use `255`. Integer codes still accept 0 to 255
(inclusive), encoded as unsigned 8-bit integers, including reserved codes.
Out-of-range integers raise `OverflowError`; other types raise `TypeError`.

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
