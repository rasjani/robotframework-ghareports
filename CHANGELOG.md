# Changelog

All notable changes in this project since the first tagged release are documented in this file.

## 0.9.2 - 2026-03-31

- Added support for publishing the generated summary as a pull request comment. (#51)
- Added support for appending to an existing GitHub step summary instead of overwriting it. (#47)
- Added a warning to stderr when running inside `pabot`. (#49)
- Switched dependency management from pip/pdm to `uv`. (#50)
- Expanded unit test coverage. (#52)
- Updated the README.

## 0.9.1 - 2025-10-17

- Updated CI to test against all supported Python versions. (#44)

## 0.9.0 - 2025-10-16

- Added arguments to enable or disable individual report sections. (#42)

## 0.8.4 - 2025-09-30

- Fixed Markdown table alignments. (#38)
- Standardized generated output to always use Unix newlines. (#40)

## 0.8.1 - 2025-04-22

- Fixed table rendering when a message contained the pipe character.

## 0.8.0 - 2025-03-17

- Added support for including selected environment variables in the summary. (#36)

## 0.7.0 - 2025-03-10

- Fixed execution and tests on Windows. (#33)
- Limited the size of the generated GitHub step summary. (#35)

## 0.6.0 - 2025-01-07

- Added collapsible sections to the generated report. (#31)
- Applied assorted fixes and cleanup. (#32)
- Moved build tasks to Invoke.

## 0.5.1 - 2024-12-23

- Applied follow-up fixes after the 0.5.0 release. (#30)

## 0.5.0 - 2024-12-23

- Added the `ghareports` CLI tool. (#29)
- Updated build configuration and action concurrency settings.

## 0.4.0 - 2024-07-05

- Migrated the listener implementation to Listener V3.
- Improved example coverage, including teardown output.
- Added checks for missing variable values.

## 0.3.1 - 2024-06-30

- Added variable evaluation support. (#28)

## 0.3.0 - 2024-06-28

- Added warnings to the generated summary. (#27)
- Improved logging.
- Switched formatting and linting workflows to Ruff.
- Refreshed generated example output and related configuration.

## 0.2.0 - 2024-05-30

- Added support for generating an extra report file. (#16)
- Fixed a missing f-string in `GHAReports.py`. (#17)
- Marked the report as initialized when an external report file is used. (#18)
- Split multiline logs with `<br>` so Markdown formatting stays intact. (#22)
- Improved build setup and test configuration. (#20, #21)
- Added initial unit tests. (#15)

## 0.1.0 - 2024-01-17

- Refactored summary output generation. (#11)
- Added status icons to section headers. (#12)
- Added example Markdown output.

## 0.0.7 - 2024-01-09

- Allowed dynamic table cell widths. (#10)
- Added a direct link to the example summary.

## 0.0.6 - 2024-01-09

- Moved packaging configuration to `pyproject.toml`. (#9)
- Fixed the example task.
- Bumped GitHub Actions checkout to `v4`.
- Updated the README.

## 0.0.3 - 2022-08-26

- Initial public release.
- Added the first working implementation for GitHub Actions summaries.
- Expanded examples to generate a summary.
- Renamed the package from `GHAReports` to `GHSummary`.
- Added Unicode pass/fail markers.
- Added support for splitting long lines in tables. (#8)
- Added basic packaging support.
