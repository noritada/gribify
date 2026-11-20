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
                             np.linspace(130, 140, 4), np.arange(12.).reshape(3, 4), decimal_scale=1)
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

    def test_generating_process_string(self):
        # No aliases: choose the second Code Table 4.3 entry.
        direct = ps.GeneratingProcess(process_type='initialization',
                                      background_process=3, process_id=4)
        assigned = ps.GeneratingProcess(0, 3, 4)
        assigned.process_type = 'initialization'
        common = self.common()
        common['generating_process'] = ps.GeneratingProcess(1, 3, 4)
        expected = section4(g.ProductDefinition(g.Template4_0(**common)))
        for process in (direct, assigned):
            with self.subTest(process=process):
                self.assertEqual(process.process_type, 1)
                self.assertIsInstance(process.process_type, int)
                self.assertEqual((process.background_process, process.process_id), (3, 4))
                common['generating_process'] = process
                data = section4(g.ProductDefinition(g.Template4_0(**common)))
                self.assertEqual(data[11], 1)  # Section 4, octet 12.
                self.assertEqual(data, expected)

    def test_generating_process_integer_codes(self):
        process = ps.GeneratingProcess(0, 3, 4)
        for code in range(256):
            with self.subTest(code=code):
                self.assertEqual(ps.GeneratingProcess(code, 3, 4).process_type, code)
                process.process_type = code
                self.assertEqual(process.process_type, code)

    def test_invalid_generating_process_inputs(self):
        process = ps.GeneratingProcess(2, 3, 4)
        setters = (
            lambda value: ps.GeneratingProcess(value, 3, 4),
            lambda value: setattr(process, 'process_type', value),
        )
        for setter in setters:
            for value in ('missing', 'Missing', '', '1', 'Initialization',
                          ' initialization', 'initialization ', 'unknown'):
                with self.subTest(value=value), self.assertRaisesRegex(
                        ValueError, 'Code Table 4.3'):
                    setter(value)
            for value in (-1, 256):
                with self.subTest(value=value), self.assertRaises(OverflowError):
                    setter(value)
            for value in (None, 1.0, b'initialization', [], object()):
                with self.subTest(value=value), self.assertRaises(TypeError):
                    setter(value)
        self.assertEqual(process.process_type, 2)  # Failed assignments preserve it.

    def test_code_table_4_4_strings_and_integer_codes(self):
        # Keep integer compatibility coverage and one alias of a code with
        # multiple text representations, as required by Testing instructions.
        cases = [(code, code) for code in range(256)] + [('10 years', 5)]
        for value, code in cases:
            with self.subTest(code=code, value=value):
                common = self.common()
                common['forecast_time'] = ps.ForecastTime(5, 6, value, -12)
                forecast = section4(g.ProductDefinition(g.Template4_0(**common)))
                self.assertEqual(forecast[17], code)
                # Give each statistical unit a different value to check mapping.
                for range_unit, increment_unit, expected in (
                    (value, 255, (code, 255)),
                    (255, value, (255, code)),
                ):
                    statistical = ps.Statistical(datetime(2026, 1, 1), 0, [
                        ps.StatisticalProcess(1, 2, range_unit, 6,
                                              increment_unit, 3)])
                    data = section4(g.ProductDefinition(g.Template4_8(
                        **common, statistical=statistical)))
                    self.assertEqual((data[48], data[53]), expected)

    def test_invalid_time_unit_inputs(self):
        constructors = (
            lambda value: ps.ForecastTime(0, 0, unit=value, time=0),
            lambda value: ps.StatisticalProcess(0, 2, value, 6, 1, 1),
            lambda value: ps.StatisticalProcess(0, 2, 1, 6, value, 1),
        )
        for constructor in constructors:
            for value in ('missing', 'Missing', '', 'Minute', ' minute', 'hour ',
                          'minutes', '0', 'decade (10 years)', 'unknown'):
                with self.subTest(value=value), self.assertRaisesRegex(
                        ValueError, 'Code Table 4.4'):
                    constructor(value)
            for value in (-1, 256):
                with self.subTest(value=value), self.assertRaises(OverflowError):
                    constructor(value)
            for value in (None, 1.0, b'hour', [], object()):
                with self.subTest(value=value), self.assertRaises(TypeError):
                    constructor(value)

    def test_fixed_surface_string(self):
        # Choose the second supported Code Table 4.5 entry.
        surface = ps.FixedSurface(surface_type='entire atmosphere',
                                  scale_factor=0, scaled_value=0)
        for first in (True, False):
            with self.subTest(first=first):
                common = self.common()
                other = ps.FixedSurface(255, -127, -2147483647)
                common['horizontal'] = ps.Horizontal(
                    surface if first else other, other if first else surface)
                data = section4(g.ProductDefinition(g.Template4_0(**common)))
                self.assertEqual(data[22 if first else 28], 10)
                numeric = ps.FixedSurface(10, 0, 0)
                common['horizontal'] = ps.Horizontal(
                    numeric if first else other, other if first else numeric)
                self.assertEqual(data, section4(g.ProductDefinition(g.Template4_0(**common))))

    def test_fixed_surface_integer_codes(self):
        common = self.common()
        for code in range(256):
            with self.subTest(code=code):
                common['horizontal'] = ps.Horizontal(
                    ps.FixedSurface(code, 0, 0), ps.FixedSurface(255, -127, -2147483647))
                data = section4(g.ProductDefinition(g.Template4_0(**common)))
                self.assertEqual(data[22], code)

    def test_invalid_fixed_surface_type_inputs(self):
        for value in ('missing', 'Missing', '', '10', 'Entire atmosphere',
                      ' entire atmosphere', 'entire atmosphere ',
                      'entire atmosphere (-)', 'isobaric surface (Pa)',
                      'cloud base level', 'sigma level', 'unknown'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Code Table 4.5'):
                ps.FixedSurface(value, 0, 0)
        for value in (-1, 256):
            with self.subTest(value=value), self.assertRaises(OverflowError):
                ps.FixedSurface(value, 0, 0)
        for value in (None, 1.0, b'entire atmosphere', [], object()):
            with self.subTest(value=value), self.assertRaises(TypeError):
                ps.FixedSurface(value, 0, 0)

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
