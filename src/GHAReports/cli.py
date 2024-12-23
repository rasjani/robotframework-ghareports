from robot.api import ExecutionResult, ResultVisitor
from pathlib import Path
from GHAReports import GHAReports
import sys
import argparse


class GHAReportsVisitor(ResultVisitor):
  def __init__(self, markdown_file=None):
    self.sum = GHAReports(report_file=markdown_file)

  def start_suite(self, suite):
    self.sum.start_suite(suite, None)

  def end_suite(self, suite):
    self.sum.end_suite(suite, suite)

  def start_test(self, test):
    self.sum.start_test(test, test)

  def end_test(self, test):
    self.sum.end_test(test, test)

  def end_result(self, result):  # noqa
    self.sum.close()

  def visit_message(self, message):
    self.sum.log_message(message)


def main():
  parser = argparse.ArgumentParser(prog="ghareports")
  parser.add_argument(
    "-r", "--robotlog", default="output.xml", metavar="FILE", dest="robotlog", help="robot framework output.xml location"
  )
  parser.add_argument(
    "-m",
    "--markdown",
    default=None,
    metavar="FILE",
    dest="markdown",
    help="Write output to additional markdown file even when running from github actions",
  )

  args = parser.parse_args()

  if not Path(args.robotlog).exists():
    print(f"No robot output file found at {args.robotlog}.", file=sys.stderr)
    sys.exit(1)

  result = ExecutionResult(args.robotlog)
  visitor = None
  if args.markdown:
    visitor = GHAReportsVisitor(args.markdown)
  else:
    visitor = GHAReportsVisitor()

  result.visit(visitor)


if __name__ == "__main__":
  main()
