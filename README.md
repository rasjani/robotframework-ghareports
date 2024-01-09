robotframework-ghareports
=========================


This project enables robot framework to generate Github Job Summary for a testrun. Its a simple robot framework listener, that once
activated when RF is executed, it checks if environment variable GITHUB_STEP_SUMMARY exists and if it does, it exposes test results
to a PR - something like [this](https://github.com/rasjani/robotframework-ghareports/actions/runs/7460898688)

## Usage

Install:

```
python -mpip install robotframework-ghareports
```

Usage:

```
robot --listener GHAReports .
```


