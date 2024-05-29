robotframework-ghareports
=========================


This project enables robot framework to generate Github Job Summary for a testrun. Its a simple robot framework listener, that once
activated when RF is executed, it checks if environment variable GITHUB_STEP_SUMMARY exists and if it does, it exposes test results
to a PR - example output looks something like [this](https://github.com/rasjani/robotframework-ghareports/blob/main/example_step_summary.md)

## Usage

Install:

```shell
python -mpip install robotframework-ghareports
```

Usage:

```shell
robot --listener GHAReports .
```

If you want to limit the width of the tables in the summary, you can provide an argument to the listener like this:


```shell
robot --listener GHAReports:35 .
```

This will split each test case name at every 35 characters into a new line.

And if you want to generate the summary even  if a) you are not running in Github *or* you want to generate extra summary file independent of
Github actions, pass report_file argument to the listener like this:

```shell
robot --listener GHAReports:report_file=extra_summary.md
```
or

```shell
robot --listener GHAReports:34:extra_summary.md
```
