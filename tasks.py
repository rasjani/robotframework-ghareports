# flake8: noqa
from invoke import task, Collection
from pathlib import Path


assert Path.cwd() == Path(__file__).parent


@task
def reformat(ctx):
    print("Reformatting code with black")
    ctx.run("black src -l130 -tpy311 *.py")


@task
def black(ctx):
    print("Verifying Black conformance")
    ctx.run("black --check --diff --verbose src *.py")


@task
def ruff(ctx):
    print("Running ruff")
    ctx.run("ruff tasks.py src/")


@task(post=[black, ruff])
def check(ctx):
    print("Running all checks")


@task
def example(ctx):
    ctx.run(
        "cd example && GITHUB_STEP_SUMMARY=../example_step_summary.md robot  --nostatusrc --pythonpath ../src --listener GHAReports ."
    )


@task
def exampleci(ctx):
    ctx.run("cd example && robot  --nostatusrc --pythonpath ../src --listener GHAReports .")


@task
def test(ctx):
    ctx.run("python -m pytest utest/test*.py")
