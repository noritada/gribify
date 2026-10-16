import sys
from datetime import datetime

import numpy as np

import gribify


def main():
    lats = np.linspace(30.0, 40.0, 3)
    lngs = np.linspace(130.0, 140.0, 4)
    a = np.arange(12).astype(float).reshape(4, -1)
    discipline = 0
    ident = gribify.Identification(
        centre_id=0xFFFF,
        subcentre_id=0,
        master_table_version=29,
        local_table_version=0,
        ref_time_significance=0,
        ref_time=datetime(2026, 1, 1, 0, 0, 0),
        prod_status=0,
        data_type=0,
    )
    ps = gribify.param_set
    product = gribify.ProductDefinition(
        gribify.Template4_0(
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
        )
    )
    g = gribify.grib2_message(discipline, ident, product, lats, lngs, a)
    sys.stdout.buffer.write(g)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
