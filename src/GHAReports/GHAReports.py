# -*- coding: utf-8 -*-
import json
import os
import wrapt
from pathlib import Path
import sys
from GHAReports.mdgen import MDGen, MD_STATUSICONS
from time import time_ns
from urllib import error, request


def filter_non_requested(value):
  return value[0] is not None


@wrapt.decorator
def skip_if_not_initialized(wrapped, instance, args, kwargs):
  if not instance.initialized:
    return

  wrapped(*args, **kwargs)


def getmsts():
  return time_ns() // 1000000


def is_truthy(value):
  if isinstance(value, bool):
    return value
  if value is None:
    return False
  return str(value).strip().lower() in ("1", "true", "yes", "on")


def get_pr_number_from_event():
  event_path = os.environ.get("GITHUB_EVENT_PATH", None)
  if event_path is None:
    return None

  try:
    payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError):
    return None

  pull_request = payload.get("pull_request", None)
  if isinstance(pull_request, dict):
    return pull_request.get("number", None)

  issue = payload.get("issue", None)
  if isinstance(issue, dict) and issue.get("pull_request", None) is not None:
    return issue.get("number", None)

  return None


def get_pr_comment_context():
  token = os.environ.get("GITHUB_TOKEN", None) or os.environ.get("GH_TOKEN", None)
  repository = os.environ.get("GITHUB_REPOSITORY", None)
  event_path = os.environ.get("GITHUB_EVENT_PATH", None)
  pr_number = get_pr_number_from_event()

  missing = []
  if token is None:
    missing.append("GITHUB_TOKEN or GH_TOKEN")
  if repository is None:
    missing.append("GITHUB_REPOSITORY")
  if event_path is None:
    missing.append("GITHUB_EVENT_PATH")
  elif pr_number is None:
    missing.append("pull request number in GITHUB_EVENT_PATH payload")

  return token, repository, pr_number, missing


def github_request(url, method="GET", payload=None, token=None):
  headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "robotframework-ghareports",
  }
  data = None
  if token:
    headers["Authorization"] = f"Bearer {token}"
  if payload is not None:
    data = json.dumps(payload).encode("utf-8")
    headers["Content-Type"] = "application/json"

  req = request.Request(url, data=data, headers=headers, method=method)
  with request.urlopen(req) as response:
    return json.loads(response.read().decode("utf-8"))


def ensure_report_title(text):
  stripped = text.lstrip()
  if stripped.startswith("# Robot Framework Test Summary"):
    return text
  return f"# Robot Framework Test Summary\n\n{text}"


class GHAReports(object):
  ROBOT_LISTENER_API_VERSION = 3
  _suites = {}
  _current_case = None
  _current_suite = None
  _current_case = None
  _testcases = {}
  _output = None
  _report = None
  _append = False
  initialized = False
  summary = None
  start_ts = None
  stop_ts = None
  pr_comment = False

  # suite attributes: name test_cases  hostname id package timestamp properties file log url stdout stderr
  # case attributes: name classname elapsed_sec stdout stderr assertions timestamp status category file line log group url

  def __init__(
    self,
    cell_width_in_characters=0,
    report_file=None,
    collapsaple=True,
    as_listener=True,
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
    self._suites = {}
    self._current_case = None
    self._current_suite = None
    self._testcases = {}
    self._output = None
    self._report = None
    self._append = False
    self.initialized = False
    self.summary = None
    self.start_ts = None
    self.stop_ts = None
    self.pr_comment = False

    _pabot_index = os.environ.get("PABOTQUEUEINDEX", None)
    if _pabot_index is not None:
      p_index = None
      try:
        p_index = int(_pabot_index)
      except ValueError:
        pass
      if p_index == 0:
        print(
          "GHAReports running inside pabot is not supported. Use GHAReports during post processing output.xml", file=sys.stderr
        )
      return

    self.as_listener = as_listener
    self._output = os.environ.get("GITHUB_STEP_SUMMARY", None)

    self.cell_width_in_characters = cell_width_in_characters
    self.env_variables = env_variables

    self.include_totals = include_totals
    self.include_passes = include_passes
    self.include_skipped = include_skipped
    self.include_fails = include_fails
    self.include_warnings = include_warnings
    self.include_envs = include_envs
    self.pr_comment = is_truthy(pr_comment)
    if self._output:
      self.initialized = True
      self._output = Path(self._output).resolve()
      print(f"GHAReports detected Github environment. Generating Step Summary: {self._output!s}", file=sys.stderr)
    else:
      print("GHAReports did not detect Github environment.", file=sys.stderr)

    if report_file:
      self.initialized = True
      self._report = Path(report_file).resolve()
      print(f"GHAReports is generating extra report file @ {self._report}", file=sys.stderr)

    self.summary = MDGen(collapsaple)

    if self._output and self._output.exists() and not overwrite_summary:
      existing_summary = self._output.read_text(encoding="utf-8")
      if existing_summary.strip():
        print(f"GHAReports will append to existing summary file: {self._output!s}", file=sys.stderr)
        self.summary.write(existing_summary)
        self._append = True

  @skip_if_not_initialized
  def start_suite(self, data, result):  # noqa
    if not self.as_listener:
      if len(data.tests) > 0 and not self.start_ts:
        try:
          new_ts = data.start_time.timestamp() * 1000
          if not self.start_ts or new_ts < self.start_ts:
            self.start_ts = new_ts
        except AttributeError:
          pass
    else:
      if not self.start_ts:
        self.start_ts = getmsts()

    if len(data.tests) > 0:
      self._current_suite = data.longname
      current_suite = self._current_suite
      attrs = {}
      # TODO: create attrs from data/result
      attrs["name"] = data.name
      attrs["longname"] = data.longname
      attrs["stdout"] = []
      attrs["stderr"] = []
      self._suites[current_suite] = attrs
      self._testcases[current_suite] = {}

  @skip_if_not_initialized
  def end_suite(self, data, result):
    if not self.as_listener and len(result.tests) > 0:
      try:
        stop_ts = result.end_time.timestamp() * 1000
        if self.stop_ts is None or self.stop_ts < stop_ts:
          self.stop_ts = stop_ts
      except AttributeError:
        pass

    if len(data.tests) > 0:
      attrs = {}
      current_suite = data.longname
      attrs["name"] = data.name
      attrs["stop_ts"] = result.endtime
      # TODO: create attrs from data/result
      self._suites[current_suite].update(attrs)
      self._current_suite = None

  @skip_if_not_initialized
  def start_test(self, data, result):  # noqa
    if self._current_suite:
      self._current_case = data.longname
    current_case = data.longname
    attrs = {}
    # TODO: create attrs from data/result
    attrs["name"] = data.name
    attrs["start_ts"] = getmsts()
    attrs["stdout"] = []
    attrs["stderr"] = []
    attrs["warnings"] = []
    self._testcases[self._current_suite][current_case] = attrs

  @skip_if_not_initialized
  def end_test(self, data, result):
    current_case = data.longname
    attrs = {}
    # TODO: create attrs from data/result
    attrs["name"] = data.name
    attrs["stop_ts"] = result.endtime
    attrs["duration"] = result.elapsedtime
    attrs["suite"] = self._current_suite
    attrs["status"] = result.status
    attrs["message"] = result.message.replace("|", "&#124;")
    self._testcases[self._current_suite][current_case].update(attrs)
    self._current_case = None

  def log_message(self, message):
    if message.level == "WARN" and self._current_suite and self._current_case and message.message:
      self._testcases[self._current_suite][self._current_case]["warnings"].append(message.message)

  @skip_if_not_initialized
  def end_keyword(self, data, result):
    pass

  def _generate_report_structure(self):
    stats = {"skip": 0, "pass": 0, "fail": 0, "total": 0, "passrate": 0}
    passed = []
    failed = []
    skipped = []
    warns = []
    envs = []

    for suitename in self._testcases.keys():
      for testname in self._testcases[suitename].keys():
        stats["total"] += 1
        testcase = self._testcases[suitename][testname]
        duration = round(testcase["duration"] / 1000, 1)
        status = testcase["status"]
        if status == "PASS":
          stats["pass"] += 1
          passed.append([testcase["name"], duration, testcase["suite"]])
        elif status == "FAIL":
          failed.append([testcase["name"], testcase["message"], duration, testcase["suite"]])
          stats["fail"] += 1
        elif status == "SKIP":
          skipped.append([testcase["name"], testcase["message"], duration, testcase["suite"]])
          stats["skip"] += 1
        if len(self._testcases[suitename][testname]["warnings"]) > 0:
          warns.extend(
            list(
              map(
                lambda logrow: (testname.replace(f"{suitename}.", ""), logrow, suitename),
                self._testcases[suitename][testname]["warnings"],
              )
            )
          )
    try:
      stats["passrate"] = round(stats["pass"] / (stats["total"] - stats["skip"]) * 100, 2)
    except ZeroDivisionError:
      stats["passrate"] = 0

    if None in [self.stop_ts, self.start_ts]:
      total_duration = 0
    else:
      total_duration = round((self.stop_ts - self.start_ts) / 1000, 1)

    if self.env_variables is not None:
      for key in self.env_variables.split(","):
        val = os.environ.get(key, None)
        if val is not None:
          envs.append((key, val))

    return (
      [[stats["pass"], stats["fail"], stats["skip"], stats["total"], stats["passrate"], total_duration]],
      passed,
      failed,
      skipped,
      warns,
      envs,
    )

  def _write_pull_request_comment(self):
    if not self.pr_comment:
      return

    token, repository, pr_number, missing = get_pr_comment_context()
    if len(missing) > 0:
      print(
        "GHAReports could not publish a pull request comment because the following required context is missing: "
        + ", ".join(missing),
        file=sys.stderr,
      )
      return

    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    marker = "<!-- robotframework-ghareports -->"
    comment_body = f"{marker}\n{ensure_report_title(self.summary.full_summary.getvalue())}"
    comments_url = f"{api_url}/repos/{repository}/issues/{pr_number}/comments"

    try:
      comments = github_request(comments_url, token=token)
      existing_comment = next(
        (
          comment
          for comment in comments
          if isinstance(comment, dict) and marker in comment.get("body", "") and comment.get("user", {}).get("type") == "Bot"
        ),
        None,
      )

      if existing_comment is None:
        github_request(comments_url, method="POST", payload={"body": comment_body}, token=token)
        print(f"GHAReports created a pull request comment for PR #{pr_number}", file=sys.stderr)
      else:
        comment_url = f"{api_url}/repos/{repository}/issues/comments/{existing_comment['id']}"
        github_request(comment_url, method="PATCH", payload={"body": comment_body}, token=token)
        print(f"GHAReports updated pull request comment {existing_comment['id']} for PR #{pr_number}", file=sys.stderr)
    except error.HTTPError as exc:
      print(f"GHAReports failed to publish pull request comment: HTTP {exc.code}", file=sys.stderr)
    except error.URLError as exc:
      print(f"GHAReports failed to publish pull request comment: {exc.reason}", file=sys.stderr)

  @skip_if_not_initialized
  def close(self):
    if self.as_listener:
      self.stop_ts = getmsts()

    stats, passed, failed, skipped, warns, envs = self._generate_report_structure()

    self.summary.header("Robot Framework Test Summary", level=1)
    header_level = 2

    if self.include_totals:
      self.summary.horizontal_ruler()
      test_headers = [
        f"Passed {MD_STATUSICONS['PASS']}",
        f"Failed {MD_STATUSICONS['FAIL']}",
        f"Skipped {MD_STATUSICONS['SKIP']}",
        "Total",
        "Passrate %",
        "Duration (sec)",
      ]
      self.summary.header("Totals", level=header_level)
      self.summary.table(
        test_headers,
        stats,
        alignments=["center", "center", "center", "center", "right", "right"],
        cell_width_in_characters=self.cell_width_in_characters,
        ignore_collapsaple=True,
      )

    if len(envs) > 0 and self.include_envs:
      self.summary.header("Environment Variables", level=header_level)
      env_headers = ["Variable", "Value"]
      self.summary.table(
        env_headers,
        envs,
        alignments=["left", "right"],
        ignore_collapsaple=True,
      )

    if self.include_passes:
      self.summary.header(f"{MD_STATUSICONS['PASS']} Passing tests", level=header_level)
      self.summary.start_section()
      test_headers = ["Testcase", "Duration (sec)", "Suite"]
      self.summary.table(
        test_headers,
        passed,
        alignments=["left", "right", "left"],
        cell_width_in_characters=self.cell_width_in_characters,
      )
      self.summary.end_section()

    if self.include_fails:
      self.summary.header(f"{MD_STATUSICONS['FAIL']} Failing tests", level=header_level)
      self.summary.start_section()
      test_headers = ["Testcase", "Message", "Duration (sec)", "Suite"]
      self.summary.table(
        test_headers,
        failed,
        alignments=["left", "left", "right", "left"],
        cell_width_in_characters=self.cell_width_in_characters,
      )
      self.summary.end_section()

    if self.include_skipped:
      self.summary.header(f"{MD_STATUSICONS['SKIP']} Skipped tests", level=header_level)
      self.summary.start_section()
      test_headers = ["Testcase", "Message", "Duration (sec)", "Suite"]
      self.summary.table(
        test_headers,
        skipped,
        alignments=["left", "left", "right", "left"],
        cell_width_in_characters=self.cell_width_in_characters,
      )
      self.summary.end_section()

    if self.include_warnings and len(warns) > 0:
      self.summary.header(f"{MD_STATUSICONS['WARN']} Warnings", level=header_level)
      self.summary.start_section()
      test_headers = ["Test Case", "Message", "Suite"]
      self.summary.table(
        test_headers,
        warns,
        alignments=["left", "left", "left"],
        cell_width_in_characters=self.cell_width_in_characters,
      )
      self.summary.end_section()

    for filename, buffer in filter(
      filter_non_requested, [(self._output, self.summary.gh_summary), (self._report, self.summary.full_summary)]
    ):
      try:
        print(f"GHAReports writing a summary file to {filename}", file=sys.stderr)
        Path(filename).write_text(buffer.getvalue(), encoding="utf-8")
      except Exception as e:  # NOQA: BLE001
        print(f"GHAReports encountered an errorw while writing to {filename}:\n{e}", file=sys.stderr)

    self._write_pull_request_comment()
