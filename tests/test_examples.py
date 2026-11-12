"""Run every top-level examples/*.py script against the installed package."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class ExampleScriptsTests(unittest.TestCase):
    def test_example_scripts(self):
        scripts = sorted(EXAMPLES.glob("*.py"))
        self.assertTrue(scripts, f"No example scripts found in {EXAMPLES}")
        for script in scripts:
            with self.subTest(script=script.name):
                # Isolate imports and output files, and exercise each script's
                # __main__ entry point just as a user would run it.
                with tempfile.TemporaryDirectory(prefix="gribify-example-") as directory:
                    result = subprocess.run(
                        [sys.executable, "-I", "-X", "utf8", str(script)],
                        cwd=directory,
                        capture_output=True,
                        timeout=60,
                    )
                self.assertEqual(
                    result.returncode, 0,
                    f"{script.name} exited with {result.returncode}:\n"
                    + result.stderr.decode("utf-8", errors="replace"),
                )
                # app.py writes binary GRIB2 to stdout, not text. Check that
                # the output contains one framed message with no extra logging.
                if script.name == "app.py":
                    data = result.stdout
                    self.assertGreaterEqual(len(data), 20)
                    self.assertEqual(data[:4], b"GRIB")
                    self.assertEqual(data[7], 2)
                    self.assertEqual(int.from_bytes(data[8:16], "big"), len(data))
                    self.assertEqual(data[-4:], b"7777")
                elif script.name == "params.py":
                    self.assertIn("ProductParam", result.stdout.decode("utf-8"))
                elif script.name == "products.py":
                    lines = result.stdout.decode("utf-8").splitlines()
                    self.assertEqual(len(lines), 2)
                    self.assertTrue(all("ProductDefinition" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
