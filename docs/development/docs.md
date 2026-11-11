# Building the docs

The `docs` dependency group requires Python 3.11 or later (3.13 is tested).
Use a separate environment for documentation:

```sh
UV_PROJECT_ENVIRONMENT=.venv-docs uv run --python 3.13 --only-group docs mkdocs build --strict
```

Open `site/index.html` or `site/api.html` in a browser. HTML links use explicit
filenames so pages can be opened from disk. Search may require HTTP serving,
depending on the browser; for local preview with search and live reload, run:

```sh
UV_PROJECT_ENVIRONMENT=.venv-docs uv run --python 3.13 --only-group docs mkdocs serve
```

`uv run` installs the documentation dependencies automatically using `uv.lock`.
`--only-group docs` excludes the project and its runtime dependencies from this
environment.

The build reads Python sources and type stubs under `src/` with runtime
inspection disabled. It does not require building or importing the Rust extension.

## Editing

- Edit `docs/**/*.md` for prose, examples, and the selection of documented APIs.
- Edit `src/gribify/_gribify/*.pyi` for extension API types and descriptions.
- Edit `mkdocs.yml` for navigation and rendering options.

The API reference uses NumPy-style docstrings in the stubs. These descriptions
are also available to editors that read stub docstrings. They do not change
runtime `help()` output, which still comes from Rust's documentation comments.

HTML pages can be rebuilt with the command above.
