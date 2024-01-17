robotframework-ghareports
=========================


This project enables robot framework to generate Github Job Summary for a testrun. Its a simple robot framework listener, that once
activated when RF is executed, it checks if environment variable GITHUB_STEP_SUMMARY exists and if it does, it exposes test results
to a PR - example output looks something like [this](https://github.com/rasjani/robotframework-ghareports/blob/main/example_step_summary.md)

## Usage

Install:

```
python -mpip install robotframework-ghareports
```

Usage:

```
robot --listener GHAReports .
```

If you want to limit the width of the tables in the summary, you can provide an argument to the listener like this:


```
robot --listener GHAReports:35 .
```

This will split each test case name at every 35 characters into a new line.

