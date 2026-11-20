# Building the library

The package combines Python code in `src/gribify/` with a Rust extension in
`rust/`. Maturin builds the extension and packages it as `gribify._gribify`.
Run the commands below from the repository root.

## Prerequisites

Install these tools before setting up the Python environment:

- [uv](https://docs.astral.sh/uv/getting-started/installation/), for Python
  environments and package installation.
- [Rust and Cargo](https://www.rust-lang.org/tools/install), using rustup and
  the stable toolchain. The crate uses Rust edition 2024; use a current stable
  toolchain rather than relying on an older system installation.
- The native compiler and linker tools for your platform:
    - macOS: Xcode Command Line Tools (`xcode-select --install`).
    - Linux: the distribution's compiler/linker toolchain, such as
      `build-essential` on Debian or Ubuntu.
    - Windows: Visual Studio Build Tools with the Desktop development with C++
      workload and a Windows SDK, using the Rust MSVC toolchain.

Python 3.11 or later is required. The commands below use regular, GIL-enabled
CPython 3.13. `uv` can download this interpreter if it is not already installed.
Initial setup also needs network access to obtain Python packages and Rust crates.

Check that the command-line tools are available:

```sh
uv --version
rustc --version
cargo --version
```

## Create the development environment

Create a virtual environment in the checkout:

```sh
uv venv --python 3.13 .venv
```

Activate it on macOS or Linux (bash/zsh):

```sh
source .venv/bin/activate
```

Or activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the Maturin version range declared in `pyproject.toml`:

```sh
uv pip install "maturin>=1.14,<2.0"
```

Use this activated environment for the remaining commands.

## Build and install for development

```sh
maturin develop --manifest-path rust/Cargo.toml --uv
```

This compiles the Rust extension in the debug profile and installs gribify into
the active environment. It also installs the Python runtime dependencies,
including NumPy. Cargo resolves and builds the Rust dependencies declared in
`rust/Cargo.toml`. The `--uv` option uses `uv` for Python package installation,
so pip does not need to be installed in the environment.

Python source changes are available through the editable installation. After
changing Rust code or Rust dependencies, run the same command again to rebuild
the extension. Restart any running Python process or notebook kernel before
using the rebuilt native module.

For an optimized development build, add `--release`:

```sh
maturin develop --manifest-path rust/Cargo.toml --uv --release
```

These are the standard development workflows described in the
[Maturin local development guide](https://www.maturin.rs/local_development).

## Check the installation

Confirm that the package imports, then run the Python tests:

```sh
python -c "import gribify; print(gribify.__file__)"
python -m unittest discover -s tests -v
```

The tests use the standard-library `unittest` runner and NumPy; no separate test
runner installation is required.

The suite also executes every top-level `examples/*.py` script in a fresh
Python process and temporary working directory. New scripts in that directory
are included automatically. A nonzero exit status or a timeout fails the test;
failures identify the script and include its error output. The existing examples
also have output checks, including GRIB2 framing for `app.py`'s binary stdout.

To run only these script checks:

```sh
python -I -m unittest discover -s tests -p test_examples.py -v
```

These checks are included in the existing CI wheel-test jobs through unittest
discovery. Tests for code blocks in `docs/examples.md` remain separate.

## Build a wheel

To build an optimized wheel for the current platform without installing it:

```sh
maturin build --manifest-path rust/Cargo.toml --release --interpreter python --out dist
```

The wheel is written to `dist/`. Install the resulting file with `uv`, replacing
`<wheel-filename>` with the filename printed by Maturin:

```sh
uv pip install --force-reinstall "dist/<wheel-filename>.whl"
```

This replaces the editable installation in the active environment. To return to
source development, run `maturin develop --manifest-path rust/Cargo.toml --uv`
again.

The current Rust configuration enables PyO3's `abi3-py311` feature for regular
CPython builds. Wheels still target a particular operating system and
architecture; the CI workflow builds and tests the distribution variants,
including separate free-threaded Python builds. A local wheel build does not
produce all of those variants.

## Coordinate round-trip tests

With the extension installed and Cargo available, run
`python -m unittest discover -s tests/integration` to test memory layouts.
This builds the `decode_coordinates` Rust example and checks decoded values
by latitude and longitude for both packing methods. Cargo needs access to
the dependency sources. The ordinary Python tests remain available with
`python -m unittest discover -s tests`.

## Code table string aliases

Run these commands from the repository root. The shared definitions live in
`rust/code_tables.toml`. Each table declares its Code Table number, source URL,
unsigned encoding width (`bits`: 8, 16, or 32), and entries with a numeric `code`
and one or more accepted `names`. Names use lowercase ASCII letters, digits,
spaces, hyphens, underscores, or slashes, without leading or trailing whitespace.
Keep published aliases when updating definitions to preserve compatibility.

`rust/build.rs` uses the shared `rust/codegen` crate to validate these definitions
and generate Rust lookup functions in Cargo's `OUT_DIR`. It reruns when the TOML
changes. Generated Rust files are included by the extension and are not committed.
No network access is needed by the generator.

After changing definitions, update the committed Markdown tables:

```sh
cargo xtask codegen
```

This updates only the regions delimited by `<!-- codegen:NAME:start -->` and
`<!-- codegen:NAME:end -->` in `docs/api.md` and
`src/gribify/_gribify/param_set.pyi`, retaining docstring indentation. Semantic
prose, constraints, signatures, and examples remain hand-maintained. For a new
Code Table, add its named markers to both files and wire the generated
`lookup_NAME` function into the appropriate Rust argument conversion. The table
name must be nonempty and contain only lowercase ASCII letters, digits, and
underscores. The generated lookup returns `Option<u8>`, `Option<u16>`, or
`Option<u32>` according to `bits`.

Check generated tables without modifying files, and test the shared generator:

```sh
cargo xtask codegen --check
cargo test --manifest-path rust/Cargo.toml -p gribify-codegen --locked
```

CI runs both commands. Invalid definitions (including duplicate aliases or codes
and out-of-range codes) fail generation. Missing or malformed document markers
also fail the documentation update. Keep independent encoding tests in
`tests/test_product.py` to verify the Code Table values and their GRIB2 octet
positions; the generator's own tests check validation and document updates.
After documentation changes, also run the stub syntax checks and
`mkdocs build --strict` described in the documentation workflow.
