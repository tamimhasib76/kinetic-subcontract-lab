#!/usr/bin/env python3
"""Run every answer BAQ against the real [ErpLab] SQL Server database and write expected CSVs.

Usage on the SQL Server 2016 VM:
    export BAQ_CONNECTION_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=ErpLab;Trusted_Connection=yes;"
    python engines/baq/make_expected.py \
        --answers-dir ../kinetic-lab-vault/baq/answers \
        --expected-dir ../kinetic-lab-vault/baq/expected
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from engines.baq.compiler import BAQCompilationError
    from engines.baq.runner import BAQRunnerError, rows_to_csv, run_baq_file
    from engines.baq.schema import BAQValidationError
else:
    from .compiler import BAQCompilationError
    from .runner import BAQRunnerError, rows_to_csv, run_baq_file
    from .schema import BAQValidationError

DEFAULT_VAULT_BAQ_DIR = Path(__file__).resolve().parents[3] / "kinetic-lab-vault" / "baq"


def generate_expected_csvs(
    answers_dir: str | Path = DEFAULT_VAULT_BAQ_DIR / "answers",
    expected_dir: str | Path = DEFAULT_VAULT_BAQ_DIR / "expected",
    conn_str: str | None = None,
    env_var: str = "BAQ_CONNECTION_STRING",
    connection: Any = None,
    drill_ids: list[str] | None = None,
) -> list[tuple[str, Path, int]]:
    """Execute each answer BAQ against [ErpLab] and write `<expected_dir>/<ID>.csv`.

    Returns a list of `(drill_id, csv_path, row_count)` tuples.
    """
    ans_path = Path(answers_dir)
    exp_path = Path(expected_dir)
    if not ans_path.is_dir():
        raise FileNotFoundError(f"Answers directory not found: {ans_path}")

    if drill_ids:
        answer_files = [ans_path / f"{did.removesuffix('.json')}.json" for did in drill_ids]
        for af in answer_files:
            if not af.is_file():
                raise FileNotFoundError(f"Answer BAQ file not found: {af}")
    else:
        answer_files = sorted(ans_path.glob("*.json"))
        if not answer_files:
            raise FileNotFoundError(f"No answer BAQ JSON files found in: {ans_path}")

    exp_path.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, Path, int]] = []
    for ans_file in answer_files:
        drill_id = ans_file.stem
        cols, rows = run_baq_file(ans_file, conn_str=conn_str, env_var=env_var, connection=connection)
        csv_file = exp_path / f"{drill_id}.csv"
        csv_file.write_text(rows_to_csv(cols, rows), encoding="utf-8")
        results.append((drill_id, csv_file, len(rows)))

    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="make_expected.py",
        description="Run answer BAQs against [ErpLab] on SQL Server and write expected-results CSVs.",
    )
    parser.add_argument(
        "--answers-dir",
        default=str(DEFAULT_VAULT_BAQ_DIR / "answers"),
        help="Directory containing answer BAQ JSON files (default: ../kinetic-lab-vault/baq/answers).",
    )
    parser.add_argument(
        "--expected-dir",
        default=str(DEFAULT_VAULT_BAQ_DIR / "expected"),
        help="Directory where expected CSV files will be written (default: ../kinetic-lab-vault/baq/expected).",
    )
    parser.add_argument(
        "--env-var",
        default="BAQ_CONNECTION_STRING",
        help="Environment variable containing the pyodbc connection string (default: BAQ_CONNECTION_STRING).",
    )
    parser.add_argument(
        "--conn-str",
        default=None,
        help="Explicit pyodbc connection string (overrides --env-var).",
    )
    parser.add_argument(
        "drills",
        nargs="*",
        help="Optional drill IDs (e.g., B01 F01). Defaults to all *.json in --answers-dir.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        generated = generate_expected_csvs(
            answers_dir=args.answers_dir,
            expected_dir=args.expected_dir,
            conn_str=args.conn_str,
            env_var=args.env_var,
            drill_ids=args.drills or None,
        )
        for drill_id, csv_path, row_cnt in generated:
            print(f"[GENERATED] {drill_id}: {csv_path} ({row_cnt} rows)")
        print(f"Generated {len(generated)} expected CSV file(s).")
        return 0
    except (BAQValidationError, BAQCompilationError, BAQRunnerError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
