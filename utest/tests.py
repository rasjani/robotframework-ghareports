import sys
import os
import contextlib
from pathlib import Path

sys.path.append(str((Path(__file__).parent / ".." / "src").resolve()))
from GHAReports import GHAReports


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
        assert r.initialized == False
        assert r._report == None
        assert r._output == None


def test_with_github():
    with modified_environ(GITHUB_STEP_SUMMARY="/foo/bar"):
        r = GHAReports()
        assert r.initialized == True
        assert r._output == Path("/foo/bar")
        assert r._report == None


def test_extra_report_file():
    with modified_environ(GITHUB_STEP_SUMMARY="/foo/bar"):
        r = GHAReports(report_file="/bar/foo")
        assert r.initialized == True
        assert r._output == Path("/foo/bar")
        assert r._report == Path("/bar/foo")


def test_writing(tmp_path):
    step_summary = tmp_path / "step_summary.md"
    extra_report = tmp_path / "extra.md"
    with modified_environ(GITHUB_STEP_SUMMARY=f"{step_summary}"):
        r = GHAReports(report_file=f"{extra_report}")
        r.close()
        assert step_summary.exists() == True
        assert extra_report.exists() == True

        assert step_summary != extra_report
