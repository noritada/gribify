"""Coordinate round trips; requires Cargo and the Rust dependency sources."""
from datetime import datetime
import unittest

import numpy as np
import gribify as g


class MemoryLayoutTests(unittest.TestCase):
    def test_values_memory_layout(self):
        # Build the independent Rust decoder once, then compare by coordinates.
        import os
        from pathlib import Path
        import subprocess

        root = Path(__file__).resolve().parents[2]
        subprocess.run(['cargo', 'build', '--manifest-path',
                        str(root / 'rust/Cargo.toml'), '--example',
                        'decode_coordinates'], check=True)
        target = Path(os.environ.get('CARGO_TARGET_DIR', root / 'rust/target'))
        decoder = target / 'debug/examples/decode_coordinates'
        if os.name == 'nt':
            decoder = decoder.with_suffix('.exe')
        rows = np.arange(12., dtype=np.float64).reshape(3, 4)
        lats = np.array([40., 35., 30.])
        lngs = np.array([130., 131., 132., 133.])
        expected = {(lat, lon): rows[j, i]
                    for j, lat in enumerate(lats) for i, lon in enumerate(lngs)}
        layouts = []
        for order in ('C', 'F'):
            for reverse_lat in (False, True):
                for reverse_lon in (False, True):
                    selection = (slice(None, None, -1 if reverse_lat else 1),
                                 slice(None, None, -1 if reverse_lon else 1))
                    storage = rows[selection].copy(order=order)
                    values = storage[selection]
                    mode = (0 if order == 'C' else 32)
                    mode |= 64 if reverse_lat else 0
                    mode |= 128 if reverse_lon else 0
                    layouts.append((f'{order}/{reverse_lat}/{reverse_lon}', values, mode))
        volume = np.full((3, 4, 2), -999.)
        volume[:, :, 0] = rows
        layouts.append(('3d-slice', volume[:, :, 0], 0))
        for packing in ('simple', 'complex'):
            for name, values, mode in layouts:
                with self.subTest(packing=packing, layout=name):
                    np.testing.assert_array_equal(values, rows)
                    ident = g.Identification(0, 0, 29, 0, 0, datetime(2026, 1, 1), 0, 0)
                    product = bytes.fromhex(
                        '00000000ffff0000000000000100000000ffffffffffffffffffffffff')
                    message = g.grib2_message(
                        0, ident, product, lats, lngs, values,
                        packing=packing, decimal_scale=0)
                    self.assertEqual(self.sections(message)[3][71], mode)
                    result = subprocess.run([str(decoder)], input=message,
                                            capture_output=True, check=True)
                    decoded = [tuple(map(float, line.split()))
                               for line in result.stdout.splitlines()]
                    self.assertEqual(len(decoded), 12)
                    self.assertEqual({(lat, lon): value for lat, lon, value in decoded},
                                     expected)

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

