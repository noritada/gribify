"""Product definitions for an ensemble member and a six-hour accumulation."""
from datetime import datetime

from gribify import ProductDefinition, Template4_1, Template4_8, param_set as ps

horizontal = ps.Horizontal(
    first_surface=ps.FixedSurface(surface_type=1, scale_factor=0, scaled_value=0),
    second_surface=ps.FixedSurface(
        surface_type=255, scale_factor=-127, scaled_value=-2147483647,
    ),
)
forecast_time = ps.ForecastTime(cutoff_hours=0, cutoff_minutes=0, unit=1, time=0)

ensemble_product = ProductDefinition(Template4_1(
    param=ps.ProductParam(category=0, num=0),
    generating_process=ps.GeneratingProcess(4, 0, 0),
    forecast_time=forecast_time,
    horizontal=horizontal,
    ensemble_forecast=ps.EnsembleForecast(
        ensemble_forecast_type=3, perturbation_num=1, num_forecasts=20,
    ),
))

accumulated_product = ProductDefinition(Template4_8(
    param=ps.ProductParam(category=1, num=8),
    generating_process=ps.GeneratingProcess(2, 0, 0),
    forecast_time=forecast_time,
    horizontal=horizontal,
    statistical=ps.Statistical(
        end_of_overall_time_interval=datetime(2026, 1, 1, 6),
        num_missing=0,
        time_ranges=[ps.StatisticalProcess(
            statistical_process_type=1,
            time_increment_type=2,
            time_range_unit=1,
            time_range_length=6,
            time_increment_unit=255,
            time_increment_length=0,
        )],
    ),
))

# Pass either product to gribify.grib2_message with discipline=0 and
# an Identification whose reference time is 2026-01-01 00:00 UTC.
if __name__ == '__main__':
    print(ensemble_product)
    print(accumulated_product)
