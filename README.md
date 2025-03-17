robotframework-ghareports
=========================


This project enables robot framework to generate Github Job Summary for a testrun. You can either use it as listener or standalone command
line tool. When executed, it checks if environment variable GITHUB_STEP_SUMMARY exists and if it does, it exposes test results
to a PR - example output looks something like [this](https://github.com/rasjani/robotframework-ghareports/blob/main/example_step_summary.md)

Main purpose for standalone tool is that with it, you can use pabot or rerun failed test cases once you have combined the logs to a single
output.xml, you can use  `ghareports` to generate the summary.

## Installation

```shell
python -mpip install robotframework-ghareports
```

## Usage as listener

```shell
robot --listener GHAReports .
```

## Usage as standalone tool

```
python -mGHARerports -r path/to/robot/output.xml
```

Help that shows all available arguments

```
ghareports --help
```

## Additional

If you want to limit the width of the tables in the summary, you can provide an argument to the listener like this:

```shell
robot --listener GHAReports:35 .
```

or
```shell
python -mGHAReports -r output.xml --width=35
```

This will split each cell with string content at every 35 characters into a new line.

And if you want to generate the summary even  if a) you are not running in Github *or* you want to generate extra summary file independent of
Github actions, pass report_file argument to the listener like this:

```shell
robot --listener GHAReports:report_file=extra_summary.md
```
or

```shell
robot --listener GHAReports:34:extra_summary.md
```

or via standalone tool:


```shell
ghareports -r output.xml -m example_step_summary.md
```

In some cases one would want to log environment variables to the summary page. For example, if same test assets are executed against different environments and env value is coming off from action's input. This can be archived by setting each input as env variable in job's env section like this:

```yaml
jobs:
  build:
    env:
      ENVIRONMENT: ${{ inputs.TEST_ENV }}
      BROWSER: ${{ inputs.DEFAULT_BROWSER }}
      RERUN_FAILED: ${{ inputs.RERUN_FAILED }}
```

and then passing a list of comma separated list to  listener or standalone tool like this:

```shell
# listener
robot --listener GHAReports:env_variables=ENVIRONMENT,BROWSER,RERUN_FAILED
```

```shell
  ghareports -r output.xml -e ENVIRONMENT,BROWSER,RERUN_FAILED
```


