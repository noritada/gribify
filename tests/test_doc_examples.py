"""Execute the Python examples as published in docs/examples.md."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


DOCUMENT = Path(__file__).resolve().parents[1] / "docs" / "examples.md"
TEMPERATURE = "Temperature at a single forecast time"
ENSEMBLE = "An ensemble member"
PRECIPITATION = "Six-hour accumulated precipitation"


def read_examples():
    """Return fenced Python blocks keyed by heading, with original line numbers."""
    examples = {}
    heading = None
    start = None
    code = []
    for line_number, line in enumerate(DOCUMENT.read_text(encoding="utf-8").splitlines(True), 1):
        if start is not None:
            if line.strip() == "```":
                if heading in examples:
                    raise AssertionError(f"Multiple Python blocks under {heading!r}; update the example tests")
                examples[heading] = (start, "".join(code))
                start = None
                code = []
            else:
                code.append(line)
        elif re.fullmatch(r"```python\s*", line):
            start = line_number + 1
        elif line.startswith("## "):
            heading = line[3:].strip()
    if start is not None:
        raise AssertionError(f"Unclosed Python block at {DOCUMENT}:{start - 1}")
    if not examples:
        raise AssertionError(f"No Python examples found in {DOCUMENT}")
    return examples


class DocumentationExamplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples = read_examples()
        # A new/renamed example must get explicit dependency and output checks.
        if set(cls.examples) != {TEMPERATURE, ENSEMBLE, PRECIPITATION}:
            raise AssertionError(f"Update example coverage for headings: {list(cls.examples)}")

    def run_examples(self, headings):
        # Keep the Markdown line numbers in Python tracebacks. Execute the exact
        # published code, not a separately maintained copy of the examples.
        lines = ["\n"] * len(DOCUMENT.read_text(encoding="utf-8").splitlines())
        for heading in headings:
            start, code = self.examples[heading]
            code_lines = code.splitlines(True)
            lines[start - 1:start - 1 + len(code_lines)] = code_lines
        with tempfile.TemporaryDirectory(prefix="gribify-doc-examples-") as directory:
            result = subprocess.run(
                [sys.executable, "-I", "-X", "utf8", "-c",
                 "import sys; exec(compile(sys.stdin.read(), sys.argv[1], 'exec'))",
                 str(DOCUMENT)],
                input="".join(lines),
                cwd=directory,
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(
                result.returncode, 0,
                f"Examples {headings} failed:\n{result.stdout}\n{result.stderr}",
            )
            return {p.name: p.read_bytes() for p in Path(directory).iterdir() if p.is_file()}

    def check_message(self, data, template, data_type, forecast_time):
        """Check framing and selected GRIB2 fields independently of gribify."""
        self.assertGreaterEqual(len(data), 20)
        self.assertEqual(data[:4], b"GRIB")
        self.assertEqual(data[6:8], bytes([0, 2]))  # Meteorological products, GRIB2.
        self.assertEqual(int.from_bytes(data[8:16], "big"), len(data))
        self.assertEqual(data[-4:], b"7777")
        sections = {}
        pos = 16
        while pos < len(data) - 4:
            size = int.from_bytes(data[pos:pos + 4], "big")
            self.assertGreaterEqual(size, 5)
            self.assertLessEqual(pos + size, len(data) - 4)
            number = data[pos + 4]
            self.assertNotIn(number, sections)
            sections[number] = data[pos:pos + size]
            pos += size
        self.assertEqual(pos, len(data) - 4)
        self.assertEqual(list(sections), [1, 3, 4, 5, 6, 7])
        self.assertEqual(sections[1][20], data_type)
        self.assertEqual(sections[1][12:19], bytes.fromhex("07ea0101000000"))
        self.assertEqual(int.from_bytes(sections[3][6:10], "big"), 12)
        self.assertEqual(int.from_bytes(sections[5][5:9], "big"), 12)
        product = sections[4]
        self.assertEqual(int.from_bytes(product[7:9], "big"), template)
        self.assertEqual(product[17], 1)  # Hours.
        self.assertEqual(int.from_bytes(product[18:22], "big"), forecast_time)
        return product

    def test_temperature_standalone(self):
        files = self.run_examples([TEMPERATURE])
        self.assertEqual(set(files), {"temperature.grib2"})
        product = self.check_message(files["temperature.grib2"], 0, 1, 6)
        self.assertEqual(product[9:11], bytes([0, 0]))  # Temperature.
        self.assertEqual(product[22:28], bytes.fromhex("670000000002"))  # 2 m.

    def test_ensemble_after_temperature(self):
        files = self.run_examples([TEMPERATURE, ENSEMBLE])
        self.assertEqual(set(files), {"temperature.grib2", "temperature-member-1.grib2"})
        self.check_message(files["temperature.grib2"], 0, 1, 6)
        product = self.check_message(files["temperature-member-1.grib2"], 1, 4, 6)
        self.assertEqual(product[9:11], bytes([0, 0]))
        self.assertEqual(product[34:37], bytes([3, 1, 20]))

    def test_precipitation_without_ensemble(self):
        # The guide explicitly says the ensemble example is not required.
        files = self.run_examples([TEMPERATURE, PRECIPITATION])
        self.assertEqual(set(files), {"temperature.grib2", "precipitation-00-06.grib2"})
        self.check_message(files["temperature.grib2"], 0, 1, 6)
        product = self.check_message(files["precipitation-00-06.grib2"], 8, 1, 0)
        self.assertEqual(product[9:11], bytes([1, 8]))  # Total precipitation.
        self.assertEqual(product[34:41], bytes.fromhex("07ea0101060000"))  # End: 06 UTC.
        self.assertEqual(product[41], 1)  # One time range.
        self.assertEqual(product[46:49], bytes([1, 2, 1]))  # Accumulation, fixed run, hours.
        self.assertEqual(int.from_bytes(product[49:53], "big"), 6)
        self.assertEqual(product[53], 1)
        self.assertEqual(int.from_bytes(product[54:58], "big"), 1)

    def test_all_examples_in_page_order(self):
        files = self.run_examples(list(self.examples))
        self.assertEqual(set(files), {
            "temperature.grib2", "temperature-member-1.grib2", "precipitation-00-06.grib2",
        })
        self.check_message(files["temperature.grib2"], 0, 1, 6)
        self.check_message(files["temperature-member-1.grib2"], 1, 4, 6)
        self.check_message(files["precipitation-00-06.grib2"], 8, 1, 0)


if __name__ == "__main__":
    unittest.main()
