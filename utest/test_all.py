import sys
import os
import contextlib
import importlib
import json
from pathlib import Path

sys.path.append(str((Path(__file__).parent / ".." / "src").resolve()))
from GHAReports import GHAReports  # NOQA: E402
import platform

ghareports_module = importlib.import_module("GHAReports.GHAReports")

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
    assert step_summary.read_text(encoding="utf-8").count("# Robot Framework Test Summary") == 1
    assert extra_report.read_text(encoding="utf-8").count("# Robot Framework Test Summary") == 1


def test_with_pabot():
  with modified_environ(PABOTQUEUEINDEX="0"):
    r = GHAReports()
    assert r.initialized is False
    assert r._output is None
    assert r._report is None


def test_pr_comment_requires_pull_request_context(monkeypatch, tmp_path):
  calls = []

  def fake_request(*args, **kwargs):
    calls.append((args, kwargs))
    return []

  monkeypatch.setattr(ghareports_module, "github_request", fake_request)

  summary_file = tmp_path / "step_summary.md"
  with modified_environ(
    GITHUB_STEP_SUMMARY=f"{summary_file}",
    GITHUB_TOKEN="token",
    GITHUB_REPOSITORY="owner/repo",
    GITHUB_EVENT_PATH=str(tmp_path / "missing-event.json"),
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  assert calls == []


def test_pr_comment_missing_context_message(capsys, tmp_path):
  summary_file = tmp_path / "step_summary.md"
  with modified_environ(
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_REPOSITORY",
    "GITHUB_EVENT_PATH",
    GITHUB_STEP_SUMMARY=f"{summary_file}",
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  err = capsys.readouterr().err
  assert "GITHUB_TOKEN or GH_TOKEN" in err
  assert "GITHUB_REPOSITORY" in err
  assert "GITHUB_EVENT_PATH" in err


def test_pr_comment_creates_comment(monkeypatch, tmp_path):
  calls = []
  event_path = tmp_path / "event.json"
  event_path.write_text(json.dumps({"pull_request": {"number": 123}}), encoding="utf-8")

  def fake_request(url, method="GET", payload=None, token=None):
    calls.append({"url": url, "method": method, "payload": payload, "token": token})
    if method == "GET":
      return []
    return {"id": 456}

  monkeypatch.setattr(ghareports_module, "github_request", fake_request)

  summary_file = tmp_path / "step_summary.md"
  with modified_environ(
    GITHUB_STEP_SUMMARY=f"{summary_file}",
    GITHUB_TOKEN="token",
    GITHUB_REPOSITORY="owner/repo",
    GITHUB_EVENT_PATH=str(event_path),
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  assert len(calls) == 2
  assert calls[0]["method"] == "GET"
  assert calls[0]["url"].endswith("/repos/owner/repo/issues/123/comments")
  assert calls[1]["method"] == "POST"
  assert calls[1]["payload"]["body"].startswith("<!-- robotframework-ghareports -->")
  assert calls[1]["payload"]["body"].count("# Robot Framework Test Summary") == 1


def test_pr_comment_updates_existing_comment(monkeypatch, tmp_path):
  calls = []
  event_path = tmp_path / "event.json"
  event_path.write_text(json.dumps({"pull_request": {"number": 123}}), encoding="utf-8")

  def fake_request(url, method="GET", payload=None, token=None):
    calls.append({"url": url, "method": method, "payload": payload, "token": token})
    if method == "GET":
      return [{"id": 789, "body": "<!-- robotframework-ghareports -->\nold", "user": {"type": "Bot"}}]
    return {"id": 789}

  monkeypatch.setattr(ghareports_module, "github_request", fake_request)

  summary_file = tmp_path / "step_summary.md"
  with modified_environ(
    GITHUB_STEP_SUMMARY=f"{summary_file}",
    GITHUB_TOKEN="token",
    GITHUB_REPOSITORY="owner/repo",
    GITHUB_EVENT_PATH=str(event_path),
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  assert len(calls) == 2
  assert calls[0]["method"] == "GET"
  assert calls[1]["method"] == "PATCH"
  assert calls[1]["url"].endswith("/repos/owner/repo/issues/comments/789")


def test_pr_comment_does_not_duplicate_title_when_summary_file_exists(monkeypatch, tmp_path):
  calls = []
  event_path = tmp_path / "event.json"
  event_path.write_text(json.dumps({"pull_request": {"number": 123}}), encoding="utf-8")
  summary_file = tmp_path / "step_summary.md"
  summary_file.write_text("", encoding="utf-8")

  def fake_request(url, method="GET", payload=None, token=None):
    calls.append({"url": url, "method": method, "payload": payload, "token": token})
    if method == "GET":
      return []
    return {"id": 456}

  monkeypatch.setattr(ghareports_module, "github_request", fake_request)

  with modified_environ(
    GITHUB_STEP_SUMMARY=f"{summary_file}",
    GITHUB_TOKEN="token",
    GITHUB_REPOSITORY="owner/repo",
    GITHUB_EVENT_PATH=str(event_path),
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  assert calls[1]["payload"]["body"].count("# Robot Framework Test Summary") == 1


def test_pr_comment_reports_missing_pr_number(capsys, tmp_path):
  event_path = tmp_path / "event.json"
  event_path.write_text(json.dumps({"ref": "refs/heads/main"}), encoding="utf-8")
  summary_file = tmp_path / "step_summary.md"

  with modified_environ(
    GITHUB_STEP_SUMMARY=f"{summary_file}",
    GITHUB_TOKEN="token",
    GITHUB_REPOSITORY="owner/repo",
    GITHUB_EVENT_PATH=str(event_path),
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  err = capsys.readouterr().err
  assert "pull request number in GITHUB_EVENT_PATH payload" in err
