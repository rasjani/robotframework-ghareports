# Repository Guidelines

## Project Structure & Module Organization
Source code lives under `src/GHAReports`.

- `src/GHAReports/GHAReports.py`: listener implementation, report assembly, GitHub summary writing, PR comment publishing
- `src/GHAReports/cli.py`: standalone CLI for processing `output.xml`
- `src/GHAReports/mdgen.py`: Markdown generation helpers and GitHub summary size handling
- `src/GHAReports/__main__.py`: `python -m GHAReports` entry point
- `utest/test_all.py`: unit tests
- `example/`: Robot Framework demo suites and resources used for manual validation
- `.github/workflows/tests.yaml`: CI workflow
- `tasks.py`: invoke tasks used locally and in CI

Keep distribution artifacts in `dist/`. Do not move invoke tasks out of the repository root unless CI is updated with the same change.

## Build, Test, and Development Commands
This project uses `uv` for dependency management and `uv_build` as the build backend.

Common commands:

- `uv sync --locked --all-extras --dev`: install the development environment
- `uv run inv formatcheck`: verify Ruff formatting
- `uv run inv ruff`: run Ruff lint checks
- `uv run python -m pytest`: run unit tests
- `uv run inv test`: same test suite through Invoke
- `uv build`: build source and wheel distributions into `dist/`

Manual validation commands:

- `uv run inv example`: run the demo suite and regenerate `example_step_summary.md`
- `uv run inv examplecilistener`: validate listener mode locally
- `uv run inv examplecicli`: validate CLI mode locally

If you need to inspect generated Markdown locally, set:

```bash
export GITHUB_STEP_SUMMARY=$(pwd)/example_summary.md
```

## Coding Style & Naming Conventions
Code is Python-only.

- Follow Ruff configuration from `pyproject.toml`: 130-character lines, 2-space indentation, double quotes
- Use snake_case for modules and functions
- Use PascalCase for classes
- Name tests with `test_...`
- Keep listener and CLI logic in small helper functions where possible

Preferred formatting and lint commands:

```bash
uv run ruff format src/ utest/ tasks.py
uv run ruff check src/ utest/ tasks.py
```

## Testing Guidelines
Unit tests live in `utest/test_all.py`. Add regression tests there for:

- CLI flags and argument handling
- summary file generation
- PR comment behavior and GitHub context handling
- Markdown rendering edge cases such as title duplication, append behavior, and long cell wrapping

When behavior changes affect human-readable output, also validate against the Robot examples under `example/`.

Before opening a PR, run:

```bash
uv run inv formatcheck
uv run inv ruff
uv run python -m pytest
```

If the change affects rendered output, also run at least one relevant `invoke example*` task.

## GitHub Actions And Reporting Notes
This repository supports both GitHub step summaries and optional PR comments.

Important constraints:

- `GITHUB_STEP_SUMMARY` may already exist as an empty file in Actions
- PR comment publishing requires `GITHUB_TOKEN` or `GH_TOKEN`
- PR comment publishing also requires `GITHUB_REPOSITORY`, `GITHUB_EVENT_PATH`, and pull request context in the event payload
- Workflow permissions must include `pull-requests: write` when posting PR comments
- Direct listener use inside `pabot` is not supported; merge results first and then run `ghareports --robotlog output.xml`

When changing summary or comment generation, verify that:

- the title `Robot Framework Test Summary` appears exactly once in the GitHub summary
- the same title appears exactly once in the PR comment
- append mode does not duplicate headers

## Commit & Pull Request Guidelines
Use short imperative commit titles, for example:

- `Add pull request comment publishing`
- `Fix duplicate summary title`

In pull requests:

- describe the behavior change clearly
- mention new CLI flags, listener arguments, or environment requirements
- include an example command when user-facing behavior changes
- link or regenerate sample Markdown when output changes

Reference issues in the body with `Fixes #NN` when applicable.

## Security & Configuration Tips

- Never hard-code secrets
- Use GitHub Actions environment variables for runtime context
- Treat `GITHUB_TOKEN` as required only in workflows that publish PR comments
- Keep dependency changes in `pyproject.toml` and `uv.lock` aligned
- Prefer `uv sync --locked --all-extras --dev` for reproducible local environments
