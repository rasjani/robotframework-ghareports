# -*- coding: utf-8 -*-
import os
import wrapt
from pathlib import Path
import sys
from GHAReports.mdgen import MDGen, MD_STATUSICONS
from time import time_ns
from robot.libraries.BuiltIn import BuiltIn


@wrapt.decorator
def skip_if_not_initialized(wrapped, instance, args, kwargs):
  if not instance.initialized:
    return

  wrapped(*args, **kwargs)


def getmsts():
  return time_ns() // 1000000


class GHAReports(object):
  ROBOT_LISTENER_API_VERSION = 3
  _suites = {}
  _current_case = None
  _current_suite = None
  _current_case = None
  _testcases = {}
  _output = None
  _report = None
  _rf = None
  initialized = False
  summary = None
  start_ts = None
  stop_ts = None

  # suite attributes: name test_cases  hostname id package timestamp properties file log url stdout stderr
  # case attributes: name classname elapsed_sec stdout stderr assertions timestamp status category file line log group url

  def __init__(self, cell_width_in_characters=0, report_file=None, collapsaple=True, as_listener=True):
    self._rf = BuiltIn()
    self.as_listener = as_listener
    self._output = os.environ.get("GITHUB_STEP_SUMMARY", None)
    self.cell_width_in_characters = cell_width_in_characters

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
    attrs["message"] = result.message
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
    return (
      [[stats["pass"], stats["fail"], stats["skip"], stats["total"], stats["passrate"], total_duration]],
      passed,
      failed,
      skipped,
      warns,
    )

  @skip_if_not_initialized
  def close(self):
    if self.as_listener:
      self.stop_ts = getmsts()

    stats, passed, failed, skipped, warns = self._generate_report_structure()
    self.summary.horizontal_ruler()
    test_headers = [
      f"Passed {MD_STATUSICONS['PASS']}",
      f"Failed {MD_STATUSICONS['FAIL']}",
      f"Skipped {MD_STATUSICONS['SKIP']}",
      "Total",
      "Passrate %",
      "Duration (sec)",
    ]
    self.summary.header("Totals")
    self.summary.table(
      test_headers,
      stats,
      alignments=["center", "center", "center", "center", "right", "right"],
      cell_width_in_characters=self.cell_width_in_characters,
      ignore_collapsaple=True,
    )

    self.summary.header(f"{MD_STATUSICONS['PASS']} Passing tests")
    self.summary.start_section()
    test_headers = ["Testcase", "Duration (sec)", "Suite"]
    self.summary.table(
      test_headers,
      passed,
      alignments=["left", "right", "left"],
      cell_width_in_characters=self.cell_width_in_characters,
    )
    self.summary.end_section()
    self.summary.header(f"{MD_STATUSICONS['FAIL']} Failing tests")
    self.summary.start_section()
    test_headers = ["Testcase", "Message", "Duration (sec)", "Suite"]
    self.summary.table(
      test_headers,
      failed,
      alignments=["left", "left", "right", "left"],
      cell_width_in_characters=self.cell_width_in_characters,
    )
    self.summary.end_section()

    self.summary.header(f"{MD_STATUSICONS['SKIP']} Skipped tests")
    self.summary.start_section()
    test_headers = ["Testcase", "Message", "Duration (sec)", "Suite"]
    self.summary.table(
      test_headers,
      skipped,
      alignments=["left", "left", "right", "left"],
      cell_width_in_characters=self.cell_width_in_characters,
    )
    self.summary.end_section()

    if len(warns) > 0:
      self.summary.header(f"{MD_STATUSICONS['WARN']} Warnings")
      self.summary.start_section()
      test_headers = ["Test Case", "Message", "Suite"]
      self.summary.table(
        test_headers,
        warns,
        alignments=["left", "left", "left"],
        cell_width_in_characters=self.cell_width_in_characters,
      )
      self.summary.end_section()

    buffer = self.summary.getvalue()
    for filename in filter(bool, [self._output, self._report]):
      try:
        print(f"GHAReports writing a summary file to {filename}", file=sys.stderr)
        Path(filename).write_text(buffer, encoding="utf-8")
      except Exception as e:  # NOQA: BLE001
        print(f"GHAReports encountered an errow while writing to {filename}:\n{e}", file=sys.stderr)
