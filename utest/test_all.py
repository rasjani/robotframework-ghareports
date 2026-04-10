import sys
import os
import contextlib
import importlib
import json
import types
from pathlib import Path
from urllib import error

sys.path.append(str((Path(__file__).parent / ".." / "src").resolve()))
from GHAReports import GHAReports  # NOQA: E402
from GHAReports.mdgen import MDGen  # NOQA: E402
import platform
import pytest

ghareports_module = importlib.import_module("GHAReports.GHAReports")
mdgen_module = importlib.import_module("GHAReports.mdgen")

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


def test_invalid_pabot_queue_index_does_not_crash():
  with modified_environ(PABOTQUEUEINDEX="foo"):
    r = GHAReports(report_file="report.md")
    assert r.initialized is False
    assert r._report is None


def test_instances_do_not_share_report_state():
  first = GHAReports(report_file="first.md")
  second = GHAReports(report_file="second.md")

  first._testcases["Suite.One"] = {
    "Suite.One.Test": {
      "name": "Test",
      "duration": 100,
      "suite": "Suite.One",
      "status": "PASS",
      "message": "",
      "warnings": [],
    }
  }
  first._suites["Suite.One"] = {"name": "Suite.One"}

  assert first._testcases is not second._testcases
  assert first._suites is not second._suites
  assert second._testcases == {}
  assert second._suites == {}


def test_append_existing_summary(tmp_path):
  step_summary = tmp_path / "step_summary.md"
  step_summary.write_text("Existing summary\n", encoding="utf-8")

  with modified_environ(GITHUB_STEP_SUMMARY=f"{step_summary}"):
    r = GHAReports()
    r.close()

  content = step_summary.read_text(encoding="utf-8")
  assert content.startswith("Existing summary\n")
  assert content.count("# Robot Framework Test Summary") == 1


def test_overwrite_existing_summary(tmp_path):
  step_summary = tmp_path / "step_summary.md"
  step_summary.write_text("Existing summary\n", encoding="utf-8")

  with modified_environ(GITHUB_STEP_SUMMARY=f"{step_summary}"):
    r = GHAReports(overwrite_summary=True)
    r.close()

  content = step_summary.read_text(encoding="utf-8")
  assert "Existing summary" not in content
  assert content.count("# Robot Framework Test Summary") == 1


def test_generate_report_structure_stats_and_envs():
  r = GHAReports(report_file="dummy.md")
  r.start_ts = 1000
  r.stop_ts = 4000
  r._testcases = {
    "Suite.One": {
      "Suite.One.Pass": {
        "name": "Pass",
        "duration": 500,
        "suite": "Suite.One",
        "status": "PASS",
        "message": "",
        "warnings": [],
      },
      "Suite.One.Fail": {
        "name": "Fail",
        "duration": 1500,
        "suite": "Suite.One",
        "status": "FAIL",
        "message": "Boom &#124; busted",
        "warnings": ["warn one"],
      },
      "Suite.One.Skip": {
        "name": "Skip",
        "duration": 250,
        "suite": "Suite.One",
        "status": "SKIP",
        "message": "Skipped here",
        "warnings": [],
      },
    }
  }

  with modified_environ(ENV1="one", ENV2="two"):
    r.env_variables = "ENV1,ENV_MISSING,ENV2"
    stats, passed, failed, skipped, warns, envs = r._generate_report_structure()

  assert stats == [[1, 1, 1, 3, 50.0, 3.0]]
  assert passed == [["Pass", 0.5, "Suite.One"]]
  assert failed == [["Fail", "Boom &#124; busted", 1.5, "Suite.One"]]
  assert skipped == [["Skip", "Skipped here", 0.2, "Suite.One"]]
  assert warns == [("Fail", "warn one", "Suite.One")]
  assert envs == [("ENV1", "one"), ("ENV2", "two")]


def test_generate_report_structure_all_skipped_passrate_zero():
  r = GHAReports(report_file="dummy.md")
  r._testcases = {
    "Suite.One": {
      "Suite.One.Skip": {
        "name": "Skip",
        "duration": 100,
        "suite": "Suite.One",
        "status": "SKIP",
        "message": "Skipped here",
        "warnings": [],
      }
    }
  }

  stats, passed, failed, skipped, warns, envs = r._generate_report_structure()

  assert stats == [[0, 0, 1, 1, 0, 0]]
  assert passed == []
  assert failed == []
  assert skipped == [["Skip", "Skipped here", 0.1, "Suite.One"]]
  assert warns == []
  assert envs == []


def test_log_message_collects_only_warn_for_active_test():
  r = GHAReports(report_file="dummy.md")
  r._current_suite = "Suite.One"
  r._current_case = "Suite.One.Test"
  r._testcases = {"Suite.One": {"Suite.One.Test": {"warnings": []}}}

  warn_message = type("Msg", (), {"level": "WARN", "message": "careful"})()
  info_message = type("Msg", (), {"level": "INFO", "message": "ignore"})()
  empty_warn = type("Msg", (), {"level": "WARN", "message": ""})()

  r.log_message(warn_message)
  r.log_message(info_message)
  r.log_message(empty_warn)

  assert r._testcases["Suite.One"]["Suite.One.Test"]["warnings"] == ["careful"]


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


def test_pr_comment_uses_gh_token_fallback(monkeypatch, tmp_path):
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
    "GITHUB_TOKEN",
    GITHUB_STEP_SUMMARY=f"{summary_file}",
    GH_TOKEN="fallback-token",
    GITHUB_REPOSITORY="owner/repo",
    GITHUB_EVENT_PATH=str(event_path),
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  assert calls[0]["token"] == "fallback-token"
  assert calls[1]["token"] == "fallback-token"


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


def test_pr_comment_supports_issue_comment_event_payload(monkeypatch, tmp_path):
  calls = []
  event_path = tmp_path / "event.json"
  event_path.write_text(json.dumps({"issue": {"number": 321, "pull_request": {"url": "x"}}}), encoding="utf-8")

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

  assert calls[0]["url"].endswith("/repos/owner/repo/issues/321/comments")


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


def test_pr_comment_http_error_is_reported(monkeypatch, capsys, tmp_path):
  event_path = tmp_path / "event.json"
  event_path.write_text(json.dumps({"pull_request": {"number": 123}}), encoding="utf-8")
  summary_file = tmp_path / "step_summary.md"

  def fake_request(url, **_kwargs):
    raise error.HTTPError(url, 403, "forbidden", hdrs=None, fp=None)

  monkeypatch.setattr(ghareports_module, "github_request", fake_request)

  with modified_environ(
    GITHUB_STEP_SUMMARY=f"{summary_file}",
    GITHUB_TOKEN="token",
    GITHUB_REPOSITORY="owner/repo",
    GITHUB_EVENT_PATH=str(event_path),
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  err_output = capsys.readouterr().err
  assert "failed to publish pull request comment: HTTP 403" in err_output


def test_pr_comment_url_error_is_reported(monkeypatch, capsys, tmp_path):
  event_path = tmp_path / "event.json"
  event_path.write_text(json.dumps({"pull_request": {"number": 123}}), encoding="utf-8")
  summary_file = tmp_path / "step_summary.md"

  def fake_request(_url, **_kwargs):
    raise error.URLError("dns failed")

  monkeypatch.setattr(ghareports_module, "github_request", fake_request)

  with modified_environ(
    GITHUB_STEP_SUMMARY=f"{summary_file}",
    GITHUB_TOKEN="token",
    GITHUB_REPOSITORY="owner/repo",
    GITHUB_EVENT_PATH=str(event_path),
  ):
    r = GHAReports(pr_comment=True)
    r.close()

  err_output = capsys.readouterr().err
  assert "failed to publish pull request comment: dns failed" in err_output


def test_cli_exits_when_robotlog_missing(monkeypatch, capsys):
  robot_module = types.ModuleType("robot")
  robot_api_module = types.ModuleType("robot.api")
  robot_api_module.ExecutionResult = object
  robot_api_module.ResultVisitor = object
  robot_module.api = robot_api_module
  monkeypatch.setitem(sys.modules, "robot", robot_module)
  monkeypatch.setitem(sys.modules, "robot.api", robot_api_module)
  cli_module = importlib.import_module("GHAReports.cli")

  monkeypatch.setattr(sys, "argv", ["ghareports", "--robotlog", "missing.xml"])

  with pytest.raises(SystemExit) as excinfo:
    cli_module.main()

  assert excinfo.value.code == 1
  assert "No robot output file found at missing.xml." in capsys.readouterr().err


def test_cli_forwards_arguments(monkeypatch, tmp_path):
  calls = {}
  robotlog = tmp_path / "output.xml"
  robotlog.write_text("<robot/>", encoding="utf-8")
  robot_module = types.ModuleType("robot")
  robot_api_module = types.ModuleType("robot.api")
  robot_api_module.ExecutionResult = object
  robot_api_module.ResultVisitor = object
  robot_module.api = robot_api_module
  monkeypatch.setitem(sys.modules, "robot", robot_module)
  monkeypatch.setitem(sys.modules, "robot.api", robot_api_module)
  cli_module = importlib.import_module("GHAReports.cli")

  class FakeVisitor:
    def __init__(
      self,
      cell_width_in_characters,
      markdown_file=None,
      include_totals=True,
      include_passes=True,
      include_skipped=True,
      include_fails=True,
      include_warnings=True,
      include_envs=True,
      env_variables=None,
      overwrite_summary=False,
      pr_comment=False,
    ):
      calls["visitor_args"] = {
        "cell_width_in_characters": cell_width_in_characters,
        "markdown_file": markdown_file,
        "include_totals": include_totals,
        "include_passes": include_passes,
        "include_skipped": include_skipped,
        "include_fails": include_fails,
        "include_warnings": include_warnings,
        "include_envs": include_envs,
        "env_variables": env_variables,
        "overwrite_summary": overwrite_summary,
        "pr_comment": pr_comment,
      }

  class FakeExecutionResult:
    def __init__(self, path):
      calls["result_path"] = path

    def visit(self, visitor):
      calls["visited_with"] = visitor

  monkeypatch.setattr(cli_module, "GHAReportsVisitor", FakeVisitor)
  monkeypatch.setattr(cli_module, "ExecutionResult", FakeExecutionResult)
  monkeypatch.setattr(
    sys,
    "argv",
    [
      "ghareports",
      "--robotlog",
      str(robotlog),
      "--markdown",
      "report.md",
      "--width",
      "35",
      "--envs",
      "A,B",
      "--no-totals",
      "--no-passes",
      "--no-skipped",
      "--no-fails",
      "--no-warnings",
      "--overwrite-summary",
      "--pr-comment",
    ],
  )

  cli_module.main()

  assert calls["result_path"] == str(robotlog)
  assert calls["visitor_args"] == {
    "cell_width_in_characters": 35,
    "markdown_file": "report.md",
    "include_totals": False,
    "include_passes": False,
    "include_skipped": False,
    "include_fails": False,
    "include_warnings": False,
    "include_envs": True,
    "env_variables": "A,B",
    "overwrite_summary": True,
    "pr_comment": True,
  }
  assert isinstance(calls["visited_with"], FakeVisitor)


def test_mdgen_table_converts_newlines_and_wraps():
  md = MDGen()
  md.table(["Col"], [["line1\nline2"], ["abcdefgh"]], cell_width_in_characters=4)

  content = md.full_summary.getvalue()
  assert "line<br/>1<br/>line<br/>2" in content
  assert "abcd<br/>efgh" in content


def test_mdgen_collapsable_sections_indent_content():
  md = MDGen(collapsaple=True)
  md.start_section()
  md.table(["Name"], [["Value"]])
  md.end_section()

  content = md.full_summary.getvalue()
  assert "<details>" in content
  assert "  | Name |" in content
  assert "</details>" in content


def test_mdgen_size_limit_falls_back_to_header_only(monkeypatch):
  md = MDGen()
  monkeypatch.setattr(mdgen_module, "MAX_GH_SUMMARY_SIZE", 1)

  md.table(["Name"], [["Value"]])

  assert "| Name |" in md.gh_summary.getvalue()
  assert "Due to size limits, this section was not written to GitHub Summary report" in md.gh_summary.getvalue()
  assert "| Value |" in md.full_summary.getvalue()
