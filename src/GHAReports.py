# -*- coding: utf-8 -*-
import os
import wrapt
from pathlib import Path
import sys
from mdgen import MDGen, MD_STATUSICONS
from time import time_ns


@wrapt.decorator
def skip_if_not_initialized(wrapped, instance, args, kwargs):
    if not instance.initialized:
        return

    wrapped(*args, **kwargs)


def getmsts():
    return time_ns() // 1000000


class GHAReports(object):
    ROBOT_LISTENER_API_VERSION = 2
    _suites = {}
    _current_case = None
    _current_suite = None
    _testcases = {}
    initialized = False
    summary = None
    start_ts = None
    stop_ts = None

    # suite attributes: name test_cases  hostname id package timestamp properties file log url stdout stderr
    # case attributes: name classname elapsed_sec stdout stderr assertions timestamp status category file line log group url

    def __init__(self, cell_width_in_characters=0):
        self._output = os.environ.get("GITHUB_STEP_SUMMARY", None)
        self.cell_width_in_characters = cell_width_in_characters

        if self._output:
            self.initialized = True
            self._output = Path(self._output).resolve()
            print(f"GHAReports detected Github environment. Generating Step Summary: {str(self._output)}", file=sys.stderr)
        else:
            print("GHAReports did not detect Github environment.", file=sys.stderr)
        self.summary = MDGen()

    @skip_if_not_initialized
    def start_suite(self, name, attrs):
        if not self.start_ts:
            self.start_ts = getmsts()

        if len(attrs["tests"]) > 0:
            self._current_suite = attrs["longname"]
            current_suite = self._current_suite
            attrs["name"] = name
            attrs["stdout"] = []
            attrs["stderr"] = []
            self._suites[current_suite] = attrs
            self._testcases[current_suite] = {}

    @skip_if_not_initialized
    def end_suite(self, name, attrs):
        if len(attrs["tests"]) > 0:
            current_suite = attrs["longname"]
            attrs["name"] = name
            self._suites[current_suite].update(attrs)
            self._current_suite = None

    @skip_if_not_initialized
    def start_test(self, name, attrs):
        current_case = attrs["longname"]
        self._current_case = current_case

        attrs["name"] = name
        attrs["start_ts"] = getmsts()
        attrs["stdout"] = []
        attrs["stderr"] = []
        self._testcases[self._current_suite][current_case] = attrs

    @skip_if_not_initialized
    def end_test(self, name, attrs):
        current_case = attrs["longname"]
        self._testcases[self._current_suite][current_case].update(attrs)
        attrs["name"] = name
        attrs["stop_ts"] = getmsts()
        attrs["duration"] = attrs["stop_ts"] - self._testcases[self._current_suite][current_case]["start_ts"]
        attrs["suite"] = self._current_suite
        self._testcases[self._current_suite][current_case].update(attrs)
        self._current_case = None

    @skip_if_not_initialized
    def start_keyword(self, name, attrs):
        pass

    @skip_if_not_initialized
    def end_keyword(self, name, attrs):
        pass

    def _generate_report_structure(self):
        stats = {"skip": 0, "pass": 0, "fail": 0, "total": 0, "passrate": 0}
        passed = []
        failed = []
        skipped = []
        for suitename in self._testcases.keys():
            for testname in self._testcases[suitename].keys():
                stats["total"] += 1
                testcase = self._testcases[suitename][testname]
                duration = round(testcase["duration"] / 1000, 1)
                match testcase["status"]:
                    case "PASS":
                        stats["pass"] += 1
                        passed.append([testcase["name"], duration, testcase["suite"]])
                    case "FAIL":
                        failed.append([testcase["name"], testcase["message"], duration, testcase["suite"]])
                        stats["fail"] += 1
                    case "SKIP":
                        skipped.append([testcase["name"], testcase["message"], duration, testcase["suite"]])
                        stats["skip"] += 1

        stats["passrate"] = round(stats["pass"] / stats["total"] * 100, 2)
        total_duration = round((self.stop_ts - self.start_ts) / 1000, 1)
        return (
            [[stats["pass"], stats["fail"], stats["skip"], stats["total"], stats["passrate"], total_duration]],
            passed,
            failed,
            skipped,
        )

    @skip_if_not_initialized
    def close(self):
        self.stop_ts = getmsts()

        stats, passed, failed, skipped = self._generate_report_structure()
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
        )

        self.summary.header(f"{MD_STATUSICONS['PASS']} Passing tests")
        test_headers = ["Testcase", "Duration (sec)", "Suite"]
        self.summary.table(
            test_headers, passed, alignments=["left", "right", "left"], cell_width_in_characters=self.cell_width_in_characters
        )

        self.summary.header(f"{MD_STATUSICONS['FAIL']} Failing tests")
        test_headers = ["Testcase", "Message", "Duration (sec)", "Suite"]
        self.summary.table(
            test_headers,
            failed,
            alignments=["left", "left", "right", "left"],
            cell_width_in_characters=self.cell_width_in_characters,
        )

        self.summary.header(f"{MD_STATUSICONS['SKIP']} Skipped tests")
        test_headers = ["Testcase", "Message", "Duration (sec)", "Suite"]
        self.summary.table(
            test_headers,
            skipped,
            alignments=["left", "left", "right", "left"],
            cell_width_in_characters=self.cell_width_in_characters,
        )

        with open(self._output, "w", encoding="utf-8") as f:
            f.write(self.summary.getvalue())
