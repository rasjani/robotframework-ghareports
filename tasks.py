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
def flake8(ctx):
    print("Running Flake8")
    ctx.run("flake8 . --select=E9,F63,F7,F82 --show-source --statistics")
    ctx.run("flake8 . --exit-zero --statistics")


@task(post=[black, flake8])
def check(ctx):
    print("Running all checks")


@task
def example(ctx):
    ctx.run("cd example && GITHUB_STEP_SUMMARY=../example_step_summary.md robot  --nostatusrc --pythonpath ../src --listener GHAReports .")


@task
def test(ctx):
    print("TEST: WIP")
