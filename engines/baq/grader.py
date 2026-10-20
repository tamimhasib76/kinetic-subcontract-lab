"""Compare BAQ execution results against an expected-results CSV.

Checks:
- Missing or extra output columns (<Table>_<Field> and Calculated_<Name> [B18]).
- Row count differences.
- Cell value mismatches across numeric, date, and text columns.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .runner import format_cell_value, run_baq, run_baq_file
from .schema import BAQDefinition


@dataclass
class CellMismatch:
    row_index: int  # 1-based data row index
    column: str
    expected: str
    actual: str


@dataclass
class GradeResult:
    passed: bool
    expected_columns: list[str]
    actual_columns: list[str]
    expected_row_count: int
    actual_row_count: int
    missing_columns: list[str] = field(default_factory=list)
    extra_columns: list[str] = field(default_factory=list)
    mismatches: list[CellMismatch] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"Grade: {status}",
            f"Rows: expected {self.expected_row_count}, actual {self.actual_row_count}",
            f"Columns: expected {len(self.expected_columns)}, actual {len(self.actual_columns)}",
        ]
        if self.missing_columns:
            lines.append(
                f"Missing columns ({len(self.missing_columns)}): {', '.join(self.missing_columns)} "
                "(expected per BAQ output specification [B18])"
            )
        if self.extra_columns:
            lines.append(f"Extra columns ({len(self.extra_columns)}): {', '.join(self.extra_columns)}")
        for note in self.notes:
            lines.append(f"Note: {note}")
        if self.mismatches:
            lines.append(f"Cell mismatches ({len(self.mismatches)}):")
            for m in self.mismatches[:25]:
                lines.append(
                    f"  Row {m.row_index}, [{m.column}]: expected {m.expected!r}, got {m.actual!r}"
                )
            if len(self.mismatches) > 25:
                lines.append(f"  ... and {len(self.mismatches) - 25} more mismatch(es).")
        return "\n".join(lines)


def read_expected_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read an expected-results CSV into (columns, rows)."""
    p = Path(path)
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        rows = [{k: (v if v is not None else "") for k, v in row.items()} for row in reader]
    return columns, rows


def _normalize_scalar(val: str) -> tuple[str, Any]:
    """Normalize a cell string for comparison while preserving numeric precision."""
    s = val.strip() if isinstance(val, str) else format_cell_value(val).strip()
    if s == "" or s.upper() == "NULL":
        return ("null", "")
    low = s.lower()
    if low in ("true", "false"):
        return ("num", Decimal(1 if low == "true" else 0))
    # Try exact Decimal parse when the value looks numeric (no leading zero padding like '0012')
    if not (len(s) > 1 and s[0] == "0" and s[1].isdigit()):
        try:
            d = Decimal(s)
            return ("num", d.normalize())
        except InvalidOperation:
            pass
    return ("str", s)


def cells_equal(expected: str, actual: str, decimal_tolerance: Decimal = Decimal("0.0001")) -> bool:
    """Compare two cell strings with numeric/decimal awareness."""
    ek, ev = _normalize_scalar(expected)
    ak, av = _normalize_scalar(actual)
    if ek == "null" and ak == "null":
        return True
    if ek == "num" and ak == "num":
        if ev == av:
            return True
        # Allow tiny rounding tolerance only when neither side is zero
        if ev != 0 and av != 0 and abs(ev - av) <= decimal_tolerance:
            return True
        return False
    return ek == ak and ev == av


def _row_sort_key(row: dict[str, str], columns: list[str]) -> tuple[str, ...]:
    return tuple(str(row.get(c, "")).strip() for c in columns)


def grade_rows(
    actual_columns: list[str],
    actual_rows: list[dict[str, str]],
    expected_columns: list[str],
    expected_rows: list[dict[str, str]],
    check_order: bool = False,
) -> GradeResult:
    """Compare actual (columns, rows) against expected (columns, rows)."""
    missing_cols = [c for c in expected_columns if c not in actual_columns]
    extra_cols = [c for c in actual_columns if c not in expected_columns]
    common_cols = [c for c in expected_columns if c in actual_columns]

    notes: list[str] = []
    if len(actual_rows) != len(expected_rows):
        diff = len(actual_rows) - len(expected_rows)
        if diff > 0:
            notes.append(f"Actual result has {diff} more row(s) than expected.")
        else:
            notes.append(f"Actual result has {-diff} fewer row(s) than expected.")

    if check_order:
        exp_aligned = expected_rows
        act_aligned = actual_rows
    else:
        exp_aligned = sorted(expected_rows, key=lambda r: _row_sort_key(r, common_cols))
        act_aligned = sorted(actual_rows, key=lambda r: _row_sort_key(r, common_cols))

    mismatches: list[CellMismatch] = []
    compare_len = min(len(exp_aligned), len(act_aligned))
    for i in range(compare_len):
        er = exp_aligned[i]
        ar = act_aligned[i]
        for col in common_cols:
            ev = er.get(col, "")
            av = ar.get(col, "")
            if not cells_equal(ev, av):
                mismatches.append(
                    CellMismatch(
                        row_index=i + 1,
                        column=col,
                        expected=ev,
                        actual=av,
                    )
                )

    passed = (
        not missing_cols
        and not extra_cols
        and len(actual_rows) == len(expected_rows)
        and not mismatches
    )

    return GradeResult(
        passed=passed,
        expected_columns=expected_columns,
        actual_columns=actual_columns,
        expected_row_count=len(expected_rows),
        actual_row_count=len(actual_rows),
        missing_columns=missing_cols,
        extra_columns=extra_cols,
        mismatches=mismatches,
        notes=notes,
    )


def grade_baq(
    baq_or_path: str | Path | BAQDefinition | dict[str, Any],
    expected_csv_path: str | Path,
    conn_str: str | None = None,
    env_var: str = "BAQ_CONNECTION_STRING",
    connection: Any | None = None,
    check_order: bool = False,
) -> GradeResult:
    """Grade a BAQ JSON file (or pre-exported CSV result file) against an expected CSV."""
    expected_cols, expected_rows = read_expected_csv(expected_csv_path)

    if isinstance(baq_or_path, (str, Path)):
        p = Path(baq_or_path)
        if p.suffix.lower() == ".csv":
            actual_cols, actual_rows = read_expected_csv(p)
        else:
            actual_cols, actual_rows = run_baq_file(
                p, conn_str=conn_str, env_var=env_var, connection=connection
            )
    else:
        actual_cols, actual_rows = run_baq(
            baq_or_path, conn_str=conn_str, env_var=env_var, connection=connection
        )

    return grade_rows(
        actual_columns=actual_cols,
        actual_rows=actual_rows,
        expected_columns=expected_cols,
        expected_rows=expected_rows,
        check_order=check_order,
    )
