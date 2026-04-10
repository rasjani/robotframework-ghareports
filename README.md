# robotframework-ghareports

`robotframework-ghareports` generates a GitHub Actions job summary from Robot Framework results.

It supports two workflows:

- Use it as a Robot Framework listener during a normal `robot` run.
- Use it as a standalone CLI after execution, for example after pabot has merged results into a single `output.xml`.
- Optionally publish the generated report as a pull request comment.

The generated summary is written to `GITHUB_STEP_SUMMARY` when that environment variable is available. You can also write the same report to a separate Markdown file for local inspection or archival.

Example output: [example_step_summary.md](./example_step_summary.md)

## What It Reports

The generated Markdown can include:

- Totals: passed, failed, skipped, total, pass rate, duration
- Passing tests
- Failing tests with failure messages
- Skipped tests with skip messages
- Warnings logged during test execution
- Selected environment variables

Long table cells can be wrapped to improve readability in GitHub's summary view.

When enabled, the same Markdown can also be published to the pull request as an updatable bot comment. This is useful when the GitHub step summary size limit becomes a constraint.

## Installation

Install from PyPI:

```bash
python -m pip install robotframework-ghareports
```

The package exposes the `ghareports` command-line entry point.

## Usage

### Listener mode

Use the listener during a regular Robot Framework run:

```bash
robot --listener GHAReports path/to/tests
```

If `GITHUB_STEP_SUMMARY` is set, the listener writes directly to the GitHub Actions job summary.

### CLI mode

Use the CLI when you already have a Robot Framework `output.xml`:

```bash
ghareports --robotlog output.xml
```

You can also invoke it as a module:

```bash
python -m GHAReports --robotlog output.xml
```

CLI mode is useful when results are produced in multiple steps and combined afterward before generating the final summary.

## Writing to an Extra Markdown File

If you want a standalone Markdown report in addition to the GitHub summary, provide an output file.

Listener mode:

```bash
robot --listener GHAReports:report_file=extra_summary.md path/to/tests
```

CLI mode:

```bash
ghareports --robotlog output.xml --markdown extra_summary.md
```

This is also the recommended way to inspect output locally when you are not running inside GitHub Actions.

## Publishing as a Pull Request Comment

If the GitHub Actions step summary is too limited for your use case, you can also publish the generated report as a pull request comment.

CLI mode:

```bash
ghareports --robotlog output.xml --pr-comment
```

Listener mode:

```bash
robot --listener GHAReports:pr_comment=True path/to/tests
```

The comment is upserted using a hidden marker, so repeated runs update the same bot comment instead of creating a new one every time.

This feature requires:

- a pull request workflow context
- `GITHUB_TOKEN` or `GH_TOKEN`
- `GITHUB_REPOSITORY`
- `GITHUB_EVENT_PATH`

In GitHub Actions, make sure the workflow token has permission to write pull request comments:

```yaml
permissions:
  contents: read
  pull-requests: write
```

## Controlling Table Cell Width

To wrap long table cells after a fixed number of characters, set a width.

Listener mode:

```bash
robot --listener GHAReports:35 path/to/tests
```

CLI mode:

```bash
ghareports --robotlog output.xml --width 35
```

This is especially useful for long failure messages.

## Including Environment Variables

You can include selected environment variables in the generated summary. This is useful when the same test assets run against multiple environments or browser combinations and that context should be visible in the job summary.

Example GitHub Actions job configuration:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      ENVIRONMENT: ${{ inputs.TEST_ENV }}
      BROWSER: ${{ inputs.DEFAULT_BROWSER }}
      RERUN_FAILED: ${{ inputs.RERUN_FAILED }}
```

Listener mode:

```bash
robot --listener GHAReports:env_variables=ENVIRONMENT,BROWSER,RERUN_FAILED path/to/tests
```

CLI mode:

```bash
ghareports --robotlog output.xml --envs ENVIRONMENT,BROWSER,RERUN_FAILED
```

Only variables that exist in the environment are included.

## CLI Reference

```text
ghareports --robotlog FILE [options]
```

Common options:

- `-r`, `--robotlog FILE`: Robot Framework `output.xml` path. Default: `output.xml`
- `-m`, `--markdown FILE`: write the full report to an extra Markdown file
- `-w`, `--width N`: wrap table cell content after `N` characters
- `-e`, `--envs ENV1,ENV2,...`: include selected environment variables in the summary
- `--[no-]totals`: include or exclude totals section
- `--[no-]passes`: include or exclude passing tests section
- `--[no-]fails`: include or exclude failing tests section
- `--[no-]skipped`: include or exclude skipped tests section
- `--[no-]warnings`: include or exclude warnings section
- `--[no-]overwrite-summary`: overwrite an existing GitHub summary instead of appending to it
- `--[no-]pr-comment`: create or update a pull request comment with the generated report

See all options with:

```bash
ghareports --help
```

## GitHub Actions Example

Using the listener directly in a workflow step:

```yaml
- name: Run Robot Framework tests
  run: robot --listener GHAReports tests/
```

Generating the summary afterward from an existing result file:

```yaml
- name: Run Robot Framework tests
  run: robot tests/

- name: Publish GitHub summary
  run: ghareports --robotlog output.xml
```

## `pabot` Note

Direct listener use inside `pabot` is intentionally not supported. When `PABOTQUEUEINDEX` is detected, the listener exits without initializing.

For parallel execution, the expected workflow is:

1. Run tests with `pabot`
2. Merge results into a single `output.xml`
3. Run `ghareports --robotlog output.xml`

## Local Development

Source code lives under `src/GHAReports`. Tests are in `utest/`, and the example Robot assets are under `example/`.

Install development dependencies with your preferred toolchain, then use the repository tasks:

```bash
uv sync --locked --all-extras --dev
uv run inv formatcheck
uv run inv ruff
uv run python -m pytest
```

If you have installed `ghareports` and the development tools into an already activated virtual environment, you can omit `uv run` and invoke the commands directly because the executables are already on `PATH`.

Useful local example commands:

```bash
export GITHUB_STEP_SUMMARY=$(pwd)/example_summary.md
uv run inv example
uv run inv examplecilistener
uv run inv examplecicli
```

`invoke example` regenerates the sample summary from the demo suites. The `examplecilistener` and `examplecicli` tasks are useful when validating the listener and CLI flows locally.

## Project Layout

- `src/GHAReports/GHAReports.py`: listener implementation and summary assembly
- `src/GHAReports/cli.py`: CLI entry point for processing `output.xml`
- `src/GHAReports/mdgen.py`: Markdown generation helpers
- `utest/test_all.py`: unit tests
- `example/`: Robot Framework demo suites and resources

## License

GPLv3
