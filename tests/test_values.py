"""Check missing-value encoding through the public Python API."""
from datetime import datetime
import unittest

import numpy as np

import gribify as g


class ValuesTests(unittest.TestCase):
    def encode(self, values):
        ident = g.Identification(0, 0, 29, 0, 0, datetime(2026, 1, 1), 0, 0)
        product = bytes.fromhex(
            '00000000ffff0000000000000100000000ffffffffffffffffffffffff'
        )
        return g.grib2_message(
            0, ident, product, np.linspace(30, 40, 3),
            np.linspace(130, 140, 4), values,
        )

    def check_masked(self, values):
        original_data = values.data.copy()
        original_mask = np.ma.getmaskarray(values).copy()
        expected = np.array(values.data, copy=True, order='C')
        expected[original_mask] = np.nan
        message = self.encode(values)
        self.assertEqual(message, self.encode(expected))
        np.testing.assert_array_equal(values.data, original_data)
        np.testing.assert_array_equal(np.ma.getmaskarray(values), original_mask)

        # Check the actual GRIB2 bitmap, including pre-existing NaNs.
        present = ~np.isnan(expected.ravel())
        pos = 16
        while pos < len(message) - 4:
            length = int.from_bytes(message[pos:pos + 4], 'big')
            if message[pos + 4] == 6:
                payload = message[pos + 5:pos + length]
                if present.all():
                    self.assertEqual(payload, b'\xff')
                else:
                    self.assertEqual(payload, b'\x00' + np.packbits(present).tobytes())
                break
            pos += length
        else:
            self.fail('Section 6 missing')

    def test_partial_mask_and_nan(self):
        data = np.arange(12.).reshape(4, 3)
        data[1, 1] = np.nan
        mask = np.zeros((4, 3), dtype=bool)
        mask[0, 1] = mask[3, 2] = True
        values = np.ma.array(data, mask=mask, fill_value=-9999, hard_mask=True)
        values.data.flags.writeable = False
        self.check_masked(values)
        self.assertEqual(values.fill_value, -9999)
        self.assertTrue(values.hardmask)

    def test_scalar_masks(self):
        for mask in (np.ma.nomask, False, True):
            with self.subTest(mask=mask):
                self.check_masked(np.ma.array(np.arange(12.).reshape(4, 3), mask=mask))

    def test_noncontiguous(self):
        values = np.ma.array(np.arange(24.).reshape(4, 6), mask=False)
        values[2, 2] = np.ma.masked
        self.check_masked(values[:, ::2])

    def test_shape_validation(self):
        with self.assertRaisesRegex(RuntimeError, 'shape mismatch'):
            self.encode(np.ma.array(np.arange(12.).reshape(3, 4), mask=True))


if __name__ == '__main__':
    unittest.main()
