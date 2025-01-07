import sys
import os
import contextlib
from pathlib import Path

sys.path.append(str((Path(__file__).parent / ".." / "src").resolve()))
from GHAReports import GHAReports  # NOQA: E402
import platform

PREFIX = ""
if platform.system() == "Windows":
  PREFIX = Path.cwd().drive


@contextlib.contextmanager
def modified_environ(*remove, **update):
  env = os.environ
  update = update or {}
  remove = remove or []

  stomped = (set(update.keys()) | set(remove)) & set(env.keys())
  update_after = {k: env[k] for k in stomped}
  remove_after = frozenset(k for k in update if k not in env)

  try:
    env.update(update)
    [env.pop(k, None) for k in remove]
    yield
  finally:
    env.update(update_after)
    [env.pop(k) for k in remove_after]


def test_no_github():
  with modified_environ("GITHUB_STEP_SUMMARY"):
    r = GHAReports()
    assert r.initialized is False
    assert r._report is None
    assert r._output is None


def test_with_github():
  with modified_environ(GITHUB_STEP_SUMMARY=f"{PREFIX}/foo/bar"):
    r = GHAReports()
    assert r.initialized is True
    assert r._output == Path(f"{PREFIX}/foo/bar")
    assert r._report is None


def test_extra_report_file():
  with modified_environ(GITHUB_STEP_SUMMARY=f"{PREFIX}/foo/bar"):
    r = GHAReports(report_file=f"{PREFIX}/bar/foo")
    assert r.initialized is True
    assert r._output == Path(f"{PREFIX}/foo/bar")
    assert r._report == Path(f"{PREFIX}/bar/foo")


def test_writing(tmp_path):
  step_summary = tmp_path / "step_summary.md"
  extra_report = tmp_path / "extra.md"
  with modified_environ(GITHUB_STEP_SUMMARY=f"{step_summary}"):
    r = GHAReports(report_file=f"{extra_report}")
    r.close()
    assert step_summary.exists() is True
    assert extra_report.exists() is True

    assert step_summary != extra_report
