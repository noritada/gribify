# Examples

These examples show how to describe three kinds of forecast data and write them
to GRIB2 files. In the examples below, we are generating forecast data, but it
is also possible to generate analysis data. Use the [API reference](api.md) for
argument definitions, numeric ranges, missing-value representations, and
exceptions.

## Choose a template

| What you want to write | Template | Example |
| --- | --- | --- |
| An analysis or forecast field at a single time | [Template4_0](api.md#gribify.Template4_0) | [2 m temperature](#temperature-at-a-single-forecast-time) |
| One ensemble member at one forecast time | [Template4_1](api.md#gribify.Template4_1) | [Perturbed temperature forecast](#an-ensemble-member) |
| An accumulation or other statistic over a time interval | [Template4_8](api.md#gribify.Template4_8) | [Six-hour precipitation](#six-hour-accumulated-precipitation) |

## Temperature at a single forecast time

Write temperature at 2 m above ground, valid at 06:00 UTC on 1 January 2026,
from a forecast initialized at 00:00 UTC. The following code is a complete
example; run it in a Python environment with gribify installed. It writes
`temperature.grib2` in the current directory.

The arrays contain synthetic data. The centre and process identifiers are
placeholders; replace them with those appropriate to your data when adapting
the example.

```python
from datetime import datetime
from pathlib import Path

import numpy as np
import gribify
from gribify import param_set as ps

reference_time = datetime(2026, 1, 1, 0)  # UTC
lats = np.linspace(30.0, 40.0, 3)
lngs = np.linspace(130.0, 140.0, 4)
temperature = np.linspace(280.0, 291.0, 12).reshape(3, 4)  # K


def identification(data_type):
    return gribify.Identification(
        centre_id=65535,  # No originating centre specified in this example.
        subcentre_id=0,
        master_table_version=29,
        local_table_version=0,
        ref_time_significance=1,  # Start of forecast.
        ref_time=reference_time,
        prod_status=1,  # Test products.
        data_type=data_type,
    )


absent_surface = ps.FixedSurface(
    surface_type=255, scale_factor=-127, scaled_value=-2147483647,
)
two_metres = ps.Horizontal(
    first_surface=ps.FixedSurface(
        surface_type=103, scale_factor=0, scaled_value=2,
    ),
    second_surface=absent_surface,
)
six_hours = ps.ForecastTime(
    cutoff_hours=0, cutoff_minutes=0, unit=1, time=6,
)
forecast_process = ps.GeneratingProcess(
    process_type=2, background_process=0, process_id=0,
)

product = gribify.ProductDefinition(gribify.Template4_0(
    param=ps.ProductParam(category=0, num=0),
    generating_process=forecast_process,
    forecast_time=six_hours,
    horizontal=two_metres,
))

message = gribify.grib2_message(
    discipline=0,
    ident=identification(data_type=1),
    product=product,
    lats=lats,
    lngs=lngs,
    values=temperature,
    decimal_scale=1,
)
Path("temperature.grib2").write_bytes(message)
```

The choices that connect the data to its metadata are:

- `discipline=0` with `category=0, num=0` describes temperature; the values
  supplied here are in kelvin.
- `surface_type=103` and a value of `2` describe the height above ground.
  An absent second surface makes this a level rather than a layer.
- `unit=1, time=6` selects six hours after the reference time: 06:00 UTC.
- The values have shape `(len(lats), len(lngs))`, here `(3, 4)`.
  `decimal_scale=1` requests packing with one decimal place.

To adapt this example to analysis data, keep `Template4_0` and use the analysis
time as the reference time with a zero forecast offset (`time=0`). Set the
identification and generating-process metadata to describe an analysis, and
supply the analyzed temperature values instead of forecast values. In
particular, update the forecast-specific settings in the `identification`
helper as well as `forecast_process`.

For details, see [Identification](api.md#gribify.Identification),
[FixedSurface](api.md#gribify.param_set.FixedSurface),
[ForecastTime](api.md#gribify.param_set.ForecastTime), and
[grib2_message](api.md#gribify.grib2_message).

## An ensemble member

Write one perturbed ensemble member's 2 m temperature forecast at the same
06:00 UTC valid time. **Run the first example before this block**: it reuses
its imports, grid, `identification` helper, `two_metres`, and `six_hours`.

```python
member_temperature = temperature + 0.5  # Synthetic member values, in K.

ensemble_product = gribify.ProductDefinition(gribify.Template4_1(
    param=ps.ProductParam(category=0, num=0),
    generating_process=ps.GeneratingProcess(
        process_type=4, background_process=0, process_id=0,
    ),
    forecast_time=six_hours,
    horizontal=two_metres,
    ensemble_forecast=ps.EnsembleForecast(
        ensemble_forecast_type=3,
        perturbation_num=1,
        num_forecasts=20,
    ),
))

message = gribify.grib2_message(
    discipline=0,
    ident=identification(data_type=4),
    product=ensemble_product,
    lats=lats,
    lngs=lngs,
    values=member_temperature,
    decimal_scale=1,
)
Path("temperature-member-1.grib2").write_bytes(message)
```

The product describes positively perturbed member 1 of an ensemble containing
20 forecasts, using `ensemble_forecast_type=3`. Section 1 also identifies it as
a perturbed forecast through `data_type=4`. These choices follow
[Code Table 4.6](https://codes.ecmwf.int/grib/format/grib2/ctables/4/6/) and
[Code Table 1.4](https://codes.ecmwf.int/grib/format/grib2/ctables/1/4/).

This call writes only the supplied member's field. It does not generate the
other members. To write another member, construct a product with that member's
number and pass its data array. See
[EnsembleForecast](api.md#gribify.param_set.EnsembleForecast) for the full
argument definitions.

## Six-hour accumulated precipitation

Write total precipitation accumulated from 00:00 through 06:00 UTC on
1 January 2026. **Run the first example before this block**: it reuses the
imports, grid, `identification` helper, `absent_surface`, and `forecast_process`.
The ensemble example is not required.

Here, six synthetic hourly accumulation fields are summed before encoding.
Template 4.8 describes the accumulation; it does not perform the summation.
The resulting total precipitation values are in kg m⁻², following the
[WMO GRIB2 total precipitation definition](https://confluence.ecmwf.int/spaces/S2S/pages/27399606/Total%2Bprecipitation).

```python
hourly_precipitation = np.full((6, len(lats), len(lngs)), 0.5)
total_precipitation = hourly_precipitation.sum(axis=0)  # 3 kg m^-2 per point.

accumulated_product = gribify.ProductDefinition(gribify.Template4_8(
    param=ps.ProductParam(category=1, num=8),
    generating_process=forecast_process,
    forecast_time=ps.ForecastTime(
        cutoff_hours=0, cutoff_minutes=0, unit=1, time=0,
    ),
    horizontal=ps.Horizontal(
        first_surface=ps.FixedSurface(
            surface_type=1, scale_factor=0, scaled_value=0,
        ),
        second_surface=absent_surface,
    ),
    statistical=ps.Statistical(
        end_of_overall_time_interval=datetime(2026, 1, 1, 6),  # UTC
        num_missing=0,
        time_ranges=[ps.StatisticalProcess(
            statistical_process_type=1,
            time_increment_type=2,
            time_range_unit=1,
            time_range_length=6,
            time_increment_unit=1,
            time_increment_length=1,
        )],
    ),
))

message = gribify.grib2_message(
    discipline=0,
    ident=identification(data_type=1),
    product=accumulated_product,
    lats=lats,
    lngs=lngs,
    values=total_precipitation,
    decimal_scale=1,
)
Path("precipitation-00-06.grib2").write_bytes(message)
```

The time settings describe one consistent interval:

| Setting in this example | Meaning |
| --- | --- |
| Reference time: 00:00 UTC | Start of the forecast run |
| Forecast offset: 0 hours | Start of the accumulation: 00:00 UTC |
| Interval length: 6 hours | Accumulate across 00:00–06:00 UTC |
| End time: 06:00 UTC | End of the accumulation |
| Increment: 1 hour | Successive hourly fields used in the sum |

`statistical_process_type=1` selects accumulation. `time_increment_type=2`
keeps the forecast run's start time fixed while the forecast time advances,
as specified in [Code Table 4.11](https://codes.ecmwf.int/grib/format/grib2/ctables/4/11/).

For another accumulation period, adjust the forecast offset, interval length,
end time, and input values together. Refer to
[Statistical](api.md#gribify.param_set.Statistical) and
[StatisticalProcess](api.md#gribify.param_set.StatisticalProcess) for field
specifications and supported ranges.
