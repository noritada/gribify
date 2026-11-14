"""Concurrent encoding with shared, immutable inputs (also run without the GIL)."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier
import unittest

import numpy as np
import gribify as g


class ThreadingTests(unittest.TestCase):
    def test_concurrent_encoding(self):
        ps = g.param_set
        ident = g.Identification(0, 0, 29, 0, 0, datetime(2026, 1, 1), 0, 0)
        product = g.ProductDefinition(g.Template4_0(
            ps.ProductParam(1, 8), ps.GeneratingProcess(2, 3, 4),
            ps.ForecastTime(5, 6, 1, -12),
            ps.Horizontal(ps.FixedSurface(100, -2, 850),
                          ps.FixedSurface(255, -127, -2147483647)),
        ))
        lats = np.linspace(30, 40, 3)
        lngs = np.linspace(130, 140, 4)
        values = np.arange(12., dtype=np.float64).reshape(3, 4)
        values[1, 1] = np.nan
        # Concurrent reads are supported; callers must not mutate or resize
        # input arrays while an encoding operation is using them.
        for array in (lats, lngs, values):
            array.flags.writeable = False
        expected = g.grib2_message(0, ident, product, lats, lngs, values, decimal_scale=1)
        barrier = Barrier(4, timeout=30)

        def encode(worker):
            barrier.wait()
            for _ in range(20):
                # Exercise both shared inputs and per-thread NumPy allocation.
                data = values if worker % 2 else values.copy()
                actual = g.grib2_message(0, ident, product, lats, lngs, data, decimal_scale=1)
                self.assertEqual(actual, expected)

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(encode, range(4)))
