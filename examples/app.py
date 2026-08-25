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
    product = (
        b"\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"
        + b"\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
    )
    g = gribify.grib2_message(discipline, ident, product, lats, lngs, a)
    sys.stdout.buffer.write(g)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
