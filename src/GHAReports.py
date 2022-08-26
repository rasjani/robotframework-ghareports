# -*- coding: utf-8 -*-
import os
import wrapt
from mdgen import MDGen, MD_PASSFAIL


@wrapt.decorator
def skip_if_not_initialized(wrapped, instance, args, kwargs):
    if not instance.initialized:
        return

    wrapped(*args, **kwargs)


class GHAReports(object):
    ROBOT_LISTENER_API_VERSION = 2
    _suites = {}
    _current_case = None
    _current_suite = None
    _testcases = {}
    initialized = False
    summary = None

    # suite attributes: name test_cases  hostname id package timestamp properties file log url stdout stderr
    # case attributes: name classname elapsed_sec stdout stderr assertions timestamp status category file line log group url

    def __init__(self, junit_file="junit.xml", junit_xslt="junit-9"):
        self._output = os.environ.get("GITHUB_STEP_SUMMARY", None)
        self.initialized = self._output != None  # NOQA: E711
        self.summary = MDGen()

    @skip_if_not_initialized
    def start_suite(self, name, attrs):
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
        attrs["stdout"] = []
        attrs["stderr"] = []
        self._testcases[self._current_suite][current_case] = attrs

    @skip_if_not_initialized
    def end_test(self, name, attrs):
        current_case = attrs["longname"]
        attrs["name"] = name
        self._testcases[self._current_suite][current_case].update(attrs)
        self._current_case = None

    @skip_if_not_initialized
    def start_keyword(self, name, attrs):
        pass

    @skip_if_not_initialized
    def end_keyword(self, name, attrs):
        pass

    @skip_if_not_initialized
    def close(self):
        self.summary.horizontal_ruler()
        test_headers = ["Testcase", "Status"]
        alignments = ["left", "right"]
        for suitename in self._testcases.keys():
            self.summary.header(suitename)
            cases = []
            cells = []
            for testname in self._testcases[suitename].keys():
                testcase = self._testcases[suitename][testname]
                cells = [testcase["originalname"], MD_PASSFAIL[testcase["status"]]]
                cases.append(cells)

            self.summary.table(test_headers, cases, alignments, 15)

        with open(self._output, "w") as f:
            f.write(self.summary.getvalue())
