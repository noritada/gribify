import sys
from datetime import datetime

import numpy as np

import gribify


def main():
    lats = np.linspace(30.0, 40.0, 3)
    lngs = np.linspace(130.0, 140.0, 4)
    a = np.arange(12).astype(float).reshape(4, -1)
    product = (
        b"\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"
        + b"\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
    )
    g = gribify.generate_grib2(datetime(2026, 1, 1, 0, 0, 0), product, lats, lngs, a)
    sys.stdout.buffer.write(g)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
