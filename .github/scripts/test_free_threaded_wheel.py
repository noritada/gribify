"""Install a version-specific wheel and test it without forcing the GIL off."""
from pathlib import Path
import subprocess
import sys
import sysconfig


def main():
    assert sysconfig.get_config_var("Py_GIL_DISABLED") == 1
    assert not sys._is_gil_enabled(), "Interpreter started with the GIL enabled"
    version = f"{sys.version_info.major}{sys.version_info.minor}"
    wheel_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
    wheels = list(wheel_dir.glob(f"*-cp{version}-cp{version}t-*.whl"))
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
assert not sys._is_gil_enabled()
suite = unittest.defaultTestLoader.discover('tests')
assert not sys._is_gil_enabled(), 'An imported extension enabled the GIL'
result = unittest.TextTestRunner(verbosity=2).run(suite)
assert not sys._is_gil_enabled(), 'An extension enabled the GIL during testing'
sys.exit(0 if result.wasSuccessful() else 1)
"""], check=True)


if __name__ == "__main__":
    main()
