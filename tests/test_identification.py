"""Code Table 1.2 strings and Section 1 reference time significance encoding."""
from datetime import datetime
import unittest

import numpy as np

import gribify as g


class IdentificationTests(unittest.TestCase):
    def identification(self, significance):
        return g.Identification(
            centre_id=0, subcentre_id=0, master_table_version=29,
            local_table_version=0, ref_time_significance=significance,
            ref_time=datetime(2026, 1, 1), prod_status=0, data_type=0,
        )

    def encode(self, significance):
        return g.grib2_message(
            'meteorological', self.identification(significance),
            bytes.fromhex('00000000ffff0000000000000100000000ffffffffffffffffffffffff'),
            np.linspace(30, 40, 3), np.linspace(130, 140, 4),
            np.arange(12.).reshape(3, 4), decimal_scale=1,
        )

    def test_string_value(self):
        # No aliases: choose the second Code Table 1.2 entry.
        message = self.encode('start of forecast')
        self.assertEqual(message[20], 1)  # Section 1 follows 16-byte Section 0.
        self.assertEqual(message[27], 1)  # Section 1, octet 12.
        self.assertEqual(message, self.encode(1))

    def test_integer_codes_remain_supported(self):
        for code in range(256):
            with self.subTest(code=code):
                self.assertEqual(self.encode(code)[27], code)

    def test_invalid_inputs(self):
        for value in ('missing', 'Missing', '', '0', 'Analysis', ' analysis',
                      'analysis ', 'forecast', 'unknown'):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'Code Table 1.2'):
                    self.identification(value)
        for value in (-1, 256):
            with self.subTest(value=value), self.assertRaises(OverflowError):
                self.identification(value)
        for value in (None, 0.0, b'analysis', [], object()):
            with self.subTest(value=value), self.assertRaises(TypeError):
                self.identification(value)


if __name__ == '__main__':
    unittest.main()
