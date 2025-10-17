from robot.api import ExecutionResult, ResultVisitor
from pathlib import Path
from GHAReports import GHAReports
import sys
import argparse


class GHAReportsVisitor(ResultVisitor):
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
  ):
    self.sum = GHAReports(
      cell_width_in_characters,
      markdown_file,
      True,
      False,
      include_totals,
      include_passes,
      include_skipped,
      include_fails,
      include_warnings,
      include_envs,
      env_variables,
    )

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
  parser.add_argument(
    "-w",
    "--width",
    default=0,
    metavar="N",
    dest="cell_width_in_characters",
    type=int,
    help="Amount of characters in single row in table cell",
  )
  parser.add_argument(
    "-e",
    "--envs",
    default=None,
    metavar="ENV1(,ENV2,...)",
    dest="envs",
    type=str,
    help="Comma separated list of environment variables to include in summary",
  )

  parser.add_argument(
    "--totals",
    default=True,
    dest="include_totals",
    action=argparse.BooleanOptionalAction,
    help="Include/exclude totals from final report",
  )

  parser.add_argument(
    "--fails",
    default=True,
    dest="include_fails",
    action=argparse.BooleanOptionalAction,
    help="Include/exclude fails from final report",
  )

  parser.add_argument(
    "--passes",
    default=True,
    dest="include_passes",
    action=argparse.BooleanOptionalAction,
    help="Include/exclude passes from final report",
  )

  parser.add_argument(
    "--skipped",
    default=True,
    dest="include_skipped",
    action=argparse.BooleanOptionalAction,
    help="Include/exclude skipped from final report",
  )

  parser.add_argument(
    "--warnings",
    default=True,
    dest="include_warnings",
    action=argparse.BooleanOptionalAction,
    help="Include/exclude logging from warnings from final report",
  )

  args = parser.parse_args()

  if not Path(args.robotlog).exists():
    print(f"No robot output file found at {args.robotlog}.", file=sys.stderr)
    sys.exit(1)

  result = ExecutionResult(args.robotlog)
  visitor = None
  if args.markdown:
    visitor = GHAReportsVisitor(
      args.cell_width_in_characters,
      markdown_file=args.markdown,
      include_totals=args.include_totals,
      include_passes=args.include_passes,
      include_skipped=args.include_skipped,
      include_fails=args.include_fails,
      include_warnings=args.include_warnings,
      env_variables=args.envs,
    )
  else:
    visitor = GHAReportsVisitor(
      args.cell_width_in_characters,
      include_totals=args.include_totals,
      include_passes=args.include_passes,
      include_skipped=args.include_skipped,
      include_fails=args.include_fails,
      include_warnings=args.include_warnings,
      env_variables=args.envs,
    )

  result.visit(visitor)


if __name__ == "__main__":
  main()
