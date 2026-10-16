"""Integration tests against GRIB2 octet layouts, run with unittest discovery."""
from datetime import datetime
import struct
import unittest

import numpy as np
import gribify as g

ps = g.param_set


def section4(product):
    ident = g.Identification(65535, 0, 29, 0, 0, datetime(2026, 1, 1), 0, 0)
    message = g.grib2_message(0, ident, product, np.linspace(30, 40, 3),
                             np.linspace(130, 140, 4), np.arange(12.).reshape(4, 3))
    assert message[:4] == b'GRIB'
    assert int.from_bytes(message[8:16], 'big') == len(message)
    assert message[-4:] == b'7777'
    pos = 16
    while pos < len(message) - 4:
        length = int.from_bytes(message[pos:pos+4], 'big')
        if message[pos+4] == 4:
            return message[pos:pos+length]
        pos += length
    raise AssertionError('Section 4 missing')


class ProductTests(unittest.TestCase):
    def common(self):
        return dict(
            param=ps.ProductParam(1, 8),
            generating_process=ps.GeneratingProcess(2, 3, 4),
            forecast_time=ps.ForecastTime(5, 6, 1, -12),
            horizontal=ps.Horizontal(ps.FixedSurface(100, -2, 850),
                                    ps.FixedSurface(255, -127, -2147483647)),
        )

    def common_bytes(self):
        return (bytes([1, 8, 2, 3, 4]) + struct.pack('>HB', 5, 6)
                + bytes([1]) + bytes.fromhex('8000000c')
                + bytes([100, 130]) + struct.pack('>I', 850) + b'\xff' * 6)

    def check_product(self, template, number, suffix=b''):
        product = g.ProductDefinition(template)
        self.assertEqual(product.template_num, number)
        payload = struct.pack('>HH', 0, number) + self.common_bytes() + suffix
        expected = struct.pack('>IB', len(payload) + 5, 4) + payload
        self.assertEqual(section4(product), expected)
        self.assertEqual(section4(payload), expected)

    def test_template_0(self):
        self.check_product(g.Template4_0(**self.common()), 0)

    def test_template_1(self):
        self.check_product(g.Template4_1(**self.common(),
                           ensemble_forecast=ps.EnsembleForecast(3, 4, 20)),
                           1, bytes([3, 4, 20]))

    def test_template_8_multiple_ranges(self):
        ranges = [ps.StatisticalProcess(1, 2, 1, 6, 255, 0),
                  ps.StatisticalProcess(0, 2, 1, 24, 1, 6)]
        statistical = ps.Statistical(datetime(2026, 2, 3, 4, 5, 6), 7, ranges)
        suffix = struct.pack('>HBBBBBBI', 2026, 2, 3, 4, 5, 6, 2, 7)
        suffix += struct.pack('>BBBIBI', 1, 2, 1, 6, 255, 0)
        suffix += struct.pack('>BBBIBI', 0, 2, 1, 24, 1, 6)
        self.check_product(g.Template4_8(**self.common(), statistical=statistical), 8, suffix)

    def test_original_payload(self):
        payload = bytes.fromhex('00000000ffff0000000000000100000000ffffffffffffffffffffffff')
        common = dict(param=ps.ProductParam(255, 255),
                      generating_process=ps.GeneratingProcess(0, 0, 0),
                      forecast_time=ps.ForecastTime(0, 0, 1, 0),
                      horizontal=ps.Horizontal(ps.FixedSurface(255, -127, -2147483647),
                                               ps.FixedSurface(255, -127, -2147483647)))
        self.assertEqual(section4(g.ProductDefinition(g.Template4_0(**common))), section4(payload))

    def test_inputs_are_copied(self):
        common = self.common()
        template = g.Template4_0(**common)
        before = section4(g.ProductDefinition(template))
        common['param'].category = 4
        self.assertEqual(section4(g.ProductDefinition(template)), before)
        self.assertNotEqual(section4(g.ProductDefinition(g.Template4_0(**common))), before)

    def test_unsigned_statistical_lengths(self):
        statistical = ps.Statistical(datetime(2026, 1, 1), 0xffffffff,
                                     [ps.StatisticalProcess(1, 2, 1, 0xffffffff, 255, 0xffffffff)])
        suffix = struct.pack('>HBBBBBBI', 2026, 1, 1, 0, 0, 0, 1, 0xffffffff)
        suffix += struct.pack('>BBBIBI', 1, 2, 1, 0xffffffff, 255, 0xffffffff)
        self.check_product(g.Template4_8(**self.common(), statistical=statistical), 8, suffix)

    def test_invalid_values(self):
        with self.assertRaises(TypeError):
            g.ProductDefinition(object())
        for count in (0, 256):
            with self.assertRaises(ValueError):
                ps.Statistical(datetime(2026, 1, 1), 0,
                               [ps.StatisticalProcess(0, 2, 1, 6, 1, 1)] * count)
        with self.assertRaises(ValueError):
            ps.ForecastTime(0, 0, 1, -2147483648)
        for factor, value in [(-128, 0), (0, -2147483648)]:
            with self.assertRaises(ValueError):
                ps.FixedSurface(100, factor, value)
        with self.assertRaises(OverflowError):
            ps.StatisticalProcess(0, 2, 1, -1, 1, 1)


if __name__ == '__main__':
    unittest.main()
