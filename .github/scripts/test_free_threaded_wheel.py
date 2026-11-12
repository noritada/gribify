"""Test 3.14t or abi3t wheels, including abi3t on GIL-enabled Python."""
import argparse
from pathlib import Path
import subprocess
import sys
import sysconfig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel_dir", nargs="?", type=Path, default=Path("dist"))
    parser.add_argument("--gil-enabled", action="store_true")
    args = parser.parse_args()
    gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED")
    gil_enabled = sys._is_gil_enabled()
    print(
        f"Python executable: {sys.executable}\n"
        f"Python version: {sys.version}\n"
        f"Py_GIL_DISABLED: {gil_disabled!r}\n"
        f"GIL enabled: {gil_enabled}",
        flush=True,
    )
    assert bool(gil_disabled) == (not args.gil_enabled), (
        f"Expected a {'GIL-enabled' if args.gil_enabled else 'free-threaded'} "
        f"Python build; Py_GIL_DISABLED={gil_disabled!r}"
    )
    assert gil_enabled == args.gil_enabled, "Unexpected initial GIL state"
    version = f"{sys.version_info.major}{sys.version_info.minor}"
    if sys.version_info >= (3, 15):
        # maturin emits the compressed abi3.abi3t tag for a wheel usable by
        # both runtime flavors. Also accept an abi3t-only tag.
        wheels = [p for p in args.wheel_dir.glob("*-cp315-*-*.whl")
                  if "abi3t" in p.name.split("-")[-2].split(".")]
    else:
        assert version == "314" and not args.gil_enabled
        wheels = list(args.wheel_dir.glob("*-cp314-cp314t-*.whl"))
    assert len(wheels) == 1, wheels
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--only-binary=:all:", str(wheels[0])],
        check=True,
    )
    # A separate isolated process ensures the installed wheel is tested and
    # detects extensions that silently re-enable the GIL during import/use.
    subprocess.run([sys.executable, "-I", "-c", """
import sys
import unittest
expected_gil = sys.argv[1] == '1'
assert sys._is_gil_enabled() == expected_gil
suite = unittest.defaultTestLoader.discover('tests')
assert sys._is_gil_enabled() == expected_gil, 'An imported extension changed the GIL state'
result = unittest.TextTestRunner(verbosity=2).run(suite)
assert sys._is_gil_enabled() == expected_gil, 'An extension changed the GIL state during testing'
sys.exit(0 if result.wasSuccessful() else 1)
""", "1" if args.gil_enabled else "0"], check=True)


if __name__ == "__main__":
    main()
