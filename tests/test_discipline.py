"""Code Table 0.0 aliases and Section 0 discipline encoding."""
from datetime import datetime
import unittest

import numpy as np

import gribify as g
from gribify._gribify import grib2_message as native_grib2_message


class DisciplineTests(unittest.TestCase):
    def setUp(self):
        self.ident = g.Identification(0, 0, 29, 0, 0, datetime(2026, 1, 1), 0, 0)
        self.product = bytes.fromhex(
            '00000000ffff0000000000000100000000ffffffffffffffffffffffff'
        )
        self.lats = np.linspace(30, 40, 3)
        self.lngs = np.linspace(130, 140, 4)
        self.values = np.arange(12.).reshape(3, 4)

    def encode(self, discipline, encoder=g.grib2_message):
        return encoder(
            discipline=discipline, ident=self.ident, product=self.product,
            lats=self.lats, lngs=self.lngs, values=self.values, decimal_scale=1,
        )

    def test_string_alias(self):
        # Choose one alias of a code with multiple text representations.
        for encoder in (g.grib2_message, native_grib2_message):
            with self.subTest(encoder=encoder):
                message = self.encode('space', encoder)
                self.assertEqual(message[:4], b'GRIB')
                self.assertEqual(message[6], 3)  # Section 0, octet 7.
                self.assertEqual(message, self.encode(3, encoder))

    def test_integer_codes_remain_supported(self):
        for code in range(256):
            with self.subTest(code=code):
                self.assertEqual(self.encode(code)[6], code)

    def test_invalid_inputs(self):
        for encoder in (g.grib2_message, native_grib2_message):
            for value in ('missing', 'Missing', '', '0', 'Meteorological',
                          'meteorological products', ' space', 'space ',
                          'formerly space', 'health and socioeconomic impacts',
                          'unknown'):
                with self.subTest(value=value, encoder=encoder):
                    with self.assertRaisesRegex(ValueError, 'Code Table 0.0'):
                        self.encode(value, encoder)
            for value in (-1, 256):
                with self.subTest(value=value, encoder=encoder):
                    with self.assertRaises(OverflowError):
                        self.encode(value, encoder)
            for value in (None, 0.0, b'meteorological', [], object()):
                with self.subTest(value=value, encoder=encoder):
                    with self.assertRaises(TypeError):
                        self.encode(value, encoder)


if __name__ == '__main__':
    unittest.main()
