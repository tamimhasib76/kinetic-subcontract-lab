#!/usr/bin/env python3
"""Command-line interface for the BAQ engine.

Commands:
    baq compile <file>
    baq run <file>
    baq grade <file> <expected.csv>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Support running directly as `python3 engines/baq/cli.py` or via `engines/baq/baq`
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from engines.baq.compiler import BAQCompilationError, compile_baq_file
    from engines.baq.grader import grade_baq
    from engines.baq.runner import BAQRunnerError, rows_to_csv, run_baq_file
    from engines.baq.schema import BAQValidationError
else:
    from .compiler import BAQCompilationError, compile_baq_file
    from .grader import grade_baq
    from .runner import BAQRunnerError, rows_to_csv, run_baq_file
    from .schema import BAQValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="baq",
        description="BAQ compiler, runner, and grader targeting [ErpLab].[Erp].* (SQL Server 2016).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # baq compile <file>
    p_compile = subparsers.add_parser(
        "compile",
        help="Compile a JSON BAQ definition file to SQL Server 2016 T-SQL.",
    )
    p_compile.add_argument("file", help="Path to the BAQ JSON file.")
    p_compile.add_argument(
        "--no-header",
        action="store_true",
        help="Omit comment header (banners and citations) from generated SQL.",
    )
    p_compile.add_argument(
        "-o",
        "--out",
        help="Optional output file path to write the compiled SQL.",
    )

    # baq run <file>
    p_run = subparsers.add_parser(
        "run",
        help="Compile and run a BAQ JSON file against SQL Server via pyodbc.",
    )
    p_run.add_argument("file", help="Path to the BAQ JSON file.")
    p_run.add_argument(
        "--env-var",
        default="BAQ_CONNECTION_STRING",
        help="Environment variable containing the pyodbc connection string (default: BAQ_CONNECTION_STRING).",
    )
    p_run.add_argument(
        "--conn-str",
        default=None,
        help="Explicit pyodbc connection string (overrides --env-var).",
    )
    p_run.add_argument(
        "-o",
        "--out",
        help="Optional output CSV file path.",
    )

    # baq grade <file> <expected.csv>
    p_grade = subparsers.add_parser(
        "grade",
        help="Compare a BAQ's results against an expected-results CSV.",
    )
    p_grade.add_argument("file", help="Path to the BAQ JSON file (or an exported actual CSV).")
    p_grade.add_argument("expected", help="Path to the expected-results CSV file.")
    p_grade.add_argument(
        "--env-var",
        default="BAQ_CONNECTION_STRING",
        help="Environment variable containing the pyodbc connection string (default: BAQ_CONNECTION_STRING).",
    )
    p_grade.add_argument(
        "--conn-str",
        default=None,
        help="Explicit pyodbc connection string (overrides --env-var).",
    )
    p_grade.add_argument(
        "--check-order",
        action="store_true",
        help="Require row order to match the expected CSV exactly.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "compile":
            sql = compile_baq_file(args.file, include_header=not args.no_header)
            if args.out:
                Path(args.out).write_text(sql + "\n", encoding="utf-8")
            else:
                print(sql)
            return 0

        if args.command == "run":
            cols, rows = run_baq_file(args.file, conn_str=args.conn_str, env_var=args.env_var)
            csv_text = rows_to_csv(cols, rows)
            if args.out:
                Path(args.out).write_text(csv_text, encoding="utf-8")
            else:
                sys.stdout.write(csv_text)
            return 0

        if args.command == "grade":
            res = grade_baq(
                args.file,
                args.expected,
                conn_str=args.conn_str,
                env_var=args.env_var,
                check_order=args.check_order,
            )
            print(res.summary())
            return 0 if res.passed else 1

    except (BAQValidationError, BAQCompilationError, BAQRunnerError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
