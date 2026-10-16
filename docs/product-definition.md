# Section 4: Product Definition

`gribify.grib2_message(..., product=..., ...)` accepts a `ProductDefinition`
containing one of these templates:

| Class | Product |
| --- | --- |
| `gribify.Template4_0` | Analysis or forecast at a single time |
| `gribify.Template4_1` | Individual ensemble member at a single time |
| `gribify.Template4_8` | Average, accumulation, or other statistical processing over time intervals |

Each template takes `param`, `generating_process`, `forecast_time`, and
`horizontal`. Template 4.1 additionally takes `ensemble_forecast`; Template 4.8
additionally takes `statistical`. All arguments can be passed by keyword.
The parameter classes below are available under `gribify.param_set`.

```python
import gribify
from gribify import param_set as ps

product = gribify.ProductDefinition(gribify.Template4_0(
    param=ps.ProductParam(category=0, num=0),
    generating_process=ps.GeneratingProcess(
        process_type=2, background_process=0, process_id=0,
    ),
    forecast_time=ps.ForecastTime(
        cutoff_hours=0, cutoff_minutes=0, unit=1, time=6,
    ),
    horizontal=ps.Horizontal(
        first_surface=ps.FixedSurface(
            surface_type=103, scale_factor=0, scaled_value=2,
        ),
        second_surface=ps.FixedSurface(
            surface_type=255, scale_factor=-127, scaled_value=-2147483647,
        ),
    ),
))
# With discipline=0, this describes temperature at 2 m, six hours after
# the reference time specified in Identification.
# Pass product to gribify.grib2_message(discipline, ident, product, lats, lngs, values).
assert product.template_num == 0
```

See [the complete writer example](../examples/app.py) and
[the ensemble and accumulation examples](../examples/products.py).

## Parameters

- `ProductParam(category, num)`: parameter category and number; their meaning
  depends on the message discipline and code-table versions in `Identification`.
- `GeneratingProcess(process_type, background_process, process_id)`: generating
  process type and centre-specific process identifiers.
- `ForecastTime(cutoff_hours, cutoff_minutes, unit, time)`: observational data
  cutoff and forecast offset from the reference time. `unit` uses Code Table 4.4
  (for example, `1` means hours). `time` supports negative offsets. For Template
  4.8, this is the start of the overall interval.
- `FixedSurface(surface_type, scale_factor, scaled_value)`: surface type from
  Code Table 4.5; the value is `scaled_value * 10**(-scale_factor)` in that
  surface type's units. For an absent second surface, use `255, -127,
  -2147483647` to encode all missing-value octets as `0xff`.
- `Horizontal(first_surface, second_surface)`: a level or the two bounds of a layer.
- `EnsembleForecast(ensemble_forecast_type, perturbation_num, num_forecasts)`:
  ensemble type from Code Table 4.6, member number, and total ensemble size.
- `Statistical(end_of_overall_time_interval, num_missing, time_ranges)`: end
  datetime, number of missing values in the statistical process, and a list of
  1–255 `StatisticalProcess` objects. The encoded range count comes from the list.
- `StatisticalProcess(statistical_process_type, time_increment_type,
  time_range_unit, time_range_length, time_increment_unit, time_increment_length)`:
  statistical operation (Code Table 4.10), increment type (Code Table 4.11),
  interval length and increment with units from Code Table 4.4. Lengths are
  unsigned 32-bit integers, including `0xffffffff` when the code tables call for
  a missing value.

Datetimes should be supplied in UTC. As with `Identification`, the datetime's
calendar fields are copied directly; timezone conversion is not performed.
Signed GRIB integers use sign-magnitude representation. Consequently, scale
factors accept -127 through 127 and signed 32-bit fields accept -2147483647
through 2147483647. Out-of-range values are rejected rather than truncated.
Code-table meanings and centre-specific identifiers remain the caller's
responsibility.

Constructors copy their inputs. Changing a `ProductParam` or `GeneratingProcess`
after constructing a template does not change that template. To change a product,
construct a new template and `ProductDefinition`.

The template number is derived automatically and exposed as `template_num`.
Trailing vertical coordinate values are not supported by this structured API;
`num_coord_values` is always zero. Existing raw Section 4 payload `bytes`
(excluding the five-octet section header) remain accepted for compatibility.

## Verification

```sh
maturin develop --manifest-path rust/Cargo.toml
.venv/bin/python -m unittest discover -s tests -v
```
