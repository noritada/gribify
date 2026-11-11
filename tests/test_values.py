"""Check missing-value encoding through the public Python API."""
from datetime import datetime
import unittest
import struct

import numpy as np

import gribify as g


class ValuesTests(unittest.TestCase):
    def encode(self, values, **kwargs):
        ident = g.Identification(0, 0, 29, 0, 0, datetime(2026, 1, 1), 0, 0)
        product = bytes.fromhex(
            '00000000ffff0000000000000100000000ffffffffffffffffffffffff'
        )
        return g.grib2_message(
            0, ident, product, np.linspace(30, 40, 3),
            np.linspace(130, 140, 4), values, **kwargs,
        )

    def check_masked(self, values):
        for packing in ("complex", "simple"):
            with self.subTest(packing=packing):
                self.check_masked_packing(values, packing)

    def check_masked_packing(self, values, packing):
        original_data = values.data.copy()
        original_mask = np.ma.getmaskarray(values).copy()
        expected = np.array(values.data, copy=True, order='C')
        expected[original_mask] = np.nan
        message = self.encode(values, packing=packing, decimal_scale=1)
        self.assertEqual(message, self.encode(expected, packing=packing, decimal_scale=1))
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

    def sections(self, message):
        self.assertEqual(message[:4], b'GRIB')
        self.assertEqual(int.from_bytes(message[8:16], 'big'), len(message))
        self.assertEqual(message[-4:], b'7777')
        sections = {}
        pos = 16
        while pos < len(message) - 4:
            length = int.from_bytes(message[pos:pos + 4], 'big')
            self.assertGreaterEqual(length, 5)
            sections[message[pos + 4]] = message[pos:pos + length]
            pos += length
        self.assertEqual(pos, len(message) - 4)
        return sections

    def test_packing_selection(self):
        values = np.arange(12.).reshape(4, 3)
        default = self.encode(values, decimal_scale=1)
        self.assertEqual(default, self.encode(values, packing="complex", decimal_scale=1))
        for packing, template in (("simple", 0), ("complex", 2)):
            with self.subTest(packing=packing):
                sections = self.sections(self.encode(values, packing=packing, decimal_scale=1))
                self.assertEqual(int.from_bytes(sections[5][9:11], 'big'), template)
                self.assertEqual(int.from_bytes(sections[5][5:9], 'big'), 12)

    def test_simple_values(self):
        for scale in (-1, 0, 1, 2, 3):
            for values in (np.linspace(-1.5, 1.8, 12).reshape(4, 3),
                           np.full((4, 3), 2.5)):
                with self.subTest(constant=bool(values.min() == values.max())):
                    sections = self.sections(self.encode(values, packing="simple", decimal_scale=scale))
                    section5 = sections[5]
                    reference = struct.unpack('>f', section5[11:15])[0]

                    def signed(data):
                        raw = int.from_bytes(data, 'big')
                        return -(raw & 0x7fff) if raw & 0x8000 else raw

                    binary_scale = signed(section5[15:17])
                    decimal_scale = signed(section5[17:19])
                    self.assertEqual(decimal_scale, scale)
                    width = section5[19]
                    bits = ''.join(f'{byte:08b}' for byte in sections[7][5:])
                    codes = [int(bits[i * width:(i + 1) * width], 2)
                             if width else 0 for i in range(12)]
                    decoded = (reference + np.array(codes) * 2. ** binary_scale) * 10. ** -decimal_scale
                    np.testing.assert_allclose(decoded, values.ravel(), atol=0.5 * 10. ** -scale, rtol=0)

    def test_decimal_scale(self):
        values = np.arange(12.).reshape(4, 3) / 8
        for packing in ("simple", "complex"):
            for scale in (-2, 0, 2, 3):
                with self.subTest(packing=packing, scale=scale):
                    sections = self.sections(self.encode(values, packing=packing,
                                                         decimal_scale=scale))
                    raw = int.from_bytes(sections[5][17:19], 'big')
                    self.assertEqual(raw, abs(scale) | (0x8000 if scale < 0 else 0))
                    self.assertNotEqual(self.encode(values, packing=packing, decimal_scale=1),
                                        self.encode(values, packing=packing, decimal_scale=scale))
            masked = np.ma.array(values, mask=values < 0.5)
            self.assertEqual(self.encode(masked, packing=packing, decimal_scale=2),
                             self.encode(masked.filled(np.nan), packing=packing, decimal_scale=2))
            for scale, error in ((-32768, ValueError), (-32769, OverflowError),
                                 (32768, OverflowError), (1.5, TypeError),
                                 (None, TypeError), ("2", TypeError)):
                with self.subTest(packing=packing, invalid_scale=scale):
                    with self.assertRaises(error):
                        self.encode(values, packing=packing, decimal_scale=scale)

    def test_decimal_scale_required(self):
        from gribify._gribify import grib2_message as native_encode

        ident = g.Identification(0, 0, 29, 0, 0, datetime(2026, 1, 1), 0, 0)
        args = (0, ident, b'', np.arange(3.), np.arange(4.),
                np.arange(12.).reshape(4, 3))
        for encode in (g.grib2_message, native_encode):
            for packing in ("simple", "complex"):
                with self.subTest(encode=encode, packing=packing):
                    with self.assertRaisesRegex(TypeError, 'decimal_scale'):
                        encode(*args, packing=packing)

    def test_invalid_packing(self):
        values = np.arange(12.).reshape(4, 3)
        for packing in ("", "Simple", "jpeg"):
            with self.subTest(packing=packing):
                with self.assertRaisesRegex(ValueError, "packing must be"):
                    self.encode(values, packing=packing, decimal_scale=1)
        for packing in (None, 0):
            with self.subTest(packing=packing):
                with self.assertRaises(TypeError):
                    self.encode(values, packing=packing, decimal_scale=1)

    def test_shape_validation(self):
        with self.assertRaisesRegex(RuntimeError, 'shape mismatch'):
            self.encode(np.ma.array(np.arange(12.).reshape(3, 4), mask=True), decimal_scale=1)


if __name__ == '__main__':
    unittest.main()
