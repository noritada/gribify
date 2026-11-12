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

## Syntax highlighting assets

Highlight.js 11.8.0 and its GitHub stylesheet are bundled under
`docs/assets/vendor/highlightjs/`. Pages load these local files instead of
contacting a CDN. The theme's built-in highlight.js loading is disabled;
`docs/assets/js/highlight-init.js` initializes the bundled library.

The [BSD-3-Clause license](../assets/vendor/highlightjs/LICENSE) and
[source URLs and checksums](../assets/vendor/highlightjs/README.txt) are included
in both the repository and the generated site. When updating the assets,
update the JavaScript and CSS together and preserve the accompanying license.

## Verify the usage examples

With the library built and installed in your Python environment, run:

```sh
python -I -m unittest discover -s tests -p test_doc_examples.py -v
```

These tests read the fenced `python` code blocks directly from
`docs/examples.md`. They execute the first example independently, each later
example with only its documented prerequisite, and all examples in page order.
Each run uses a fresh Python process and a temporary output directory. The tests
check the generated GRIB2 files and selected metadata, including template
numbers, forecast times, ensemble membership, and accumulation intervals.
They do not decode and compare every packed data value.

Keep executable examples in triple-backtick `python` blocks, one per level-two
heading. When adding or renaming an example, update the heading coverage,
prerequisites, and expected outputs in `tests/test_doc_examples.py`. Keep the
example code in the Markdown file; do not copy it into the tests. Python errors
report the Markdown filename and original line number.

The existing CI wheel-test jobs discover these tests as part of
`python -I -m unittest discover -s tests -v`, so incompatible API changes are
checked against the installed wheel as well as during local development.

## Publish to GitHub Pages

The `Documentation` workflow (`.github/workflows/docs.yml`) builds and deploys
this site on every push to `master`. Tags and pushes to other branches do not
trigger it. The build uses Python 3.13 and installs only the `docs` dependency
group from `pyproject.toml`; it does not install the library or compile Rust.
Dependencies are resolved at build time, without requiring a tracked `uv.lock`.

Before the first deployment,
[configure the pages to be published with a custom GitHub Actions workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow).
Also, the workflow uses
[a deployment environment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments#using-environments)
called `github-pages`. If the `github-pages` environment has deployment branch
restrictions, allow `master`.
