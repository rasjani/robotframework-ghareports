import sys
import os
import contextlib
from pathlib import Path
sys.path.append(Path(__file__).parent / ".." / "src")
from GHAReports import GHAReports


@contextlib.contextmanager
def set_env(**environ):
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)

def test_no_github():
  with set_env(GITHUB_STEP_SUMMARY=""):
    r = GHAReports()
    assert r.initialized == False
    #assert r._report_file == None

def test_with_github():
  with set_env(GITHUB_STEP_SUMMARY="/foo/bar"):
    r = GHAReports()
    assert r.initialized == True
    assert r._output == Path("/foo/bar")
