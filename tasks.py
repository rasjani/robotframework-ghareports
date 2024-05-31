# flake8: noqa
from invoke import task, Collection
from pathlib import Path
import os


assert Path.cwd() == Path(__file__).parent


@task
def format(ctx):
  print("Formatting with ruff")
  ctx.run("ruff format tasks.py src/ utest/")


@task
def ruff(ctx):
  print("Running ruff")
  ctx.run("ruff check tasks.py src/ utest/")


@task(post=[ruff])
def check(ctx):
  print("Running all checks")


@task
def example(ctx):
  ctx.run(
    "cd example && GITHUB_STEP_SUMMARY=../example_step_summary.md robot  --nostatusrc --pythonpath ../src --listener GHAReports ."
  )


@task
def exampleci(ctx):
  if not os.environ.get("GITHUB_STEP_SUMMARY", None):
    os.environ.update({"GITHUB_STEP_SUMMARY": str(Path.cwd() / "example_summary.md")})
  ctx.run(
    f"cd example && robot  --nostatusrc --pythonpath ../src --listener GHAReports:60:report_file={Path.cwd()}/extra_summary.md ."
  )


@task
def test(ctx):
  ctx.run("python -m pytest utest/test*.py")
