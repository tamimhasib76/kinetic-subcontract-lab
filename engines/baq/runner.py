"""Execute compiled BAQ queries against SQL Server via pyodbc.

Connection string resolution order:
1. Explicit `conn_str` parameter (if passed).
2. Environment variable specified by `env_var` (default: `BAQ_CONNECTION_STRING`,
   with fallback to `ERPLAB_CONNECTION_STRING` and `MSSQL_CONNECTION_STRING`).
"""

from __future__ import annotations

import csv
import io
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .compiler import compile_baq
from .schema import BAQDefinition, load_baq, validate_baq

DEFAULT_ENV_VARS = (
    "BAQ_CONNECTION_STRING",
    "ERPLAB_CONNECTION_STRING",
    "MSSQL_CONNECTION_STRING",
)


class BAQRunnerError(RuntimeError):
    """Raised when the BAQ runner cannot connect to SQL Server or execute the query."""


def get_connection_string(conn_str: str | None = None, env_var: str = "BAQ_CONNECTION_STRING") -> str:
    """Resolve the pyodbc connection string from an argument or environment variable."""
    if conn_str and conn_str.strip():
        return conn_str.strip()

    search_vars = [env_var] + [v for v in DEFAULT_ENV_VARS if v != env_var]
    for var in search_vars:
        val = os.environ.get(var, "").strip()
        if val:
            return val

    raise BAQRunnerError(
        f"No SQL Server connection string found. Set the {env_var} environment variable "
        "(e.g., export BAQ_CONNECTION_STRING='DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;DATABASE=ErpLab;UID=sa;PWD=...')."
    )


def format_cell_value(val: Any) -> str:
    """Format a database cell value into canonical CSV string form."""
    if val is None:
        return ""
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d") if val.hour == 0 and val.minute == 0 and val.second == 0 else val.isoformat()
    if isinstance(val, date):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, Decimal):
        return str(val)
    return str(val)


def run_baq(
    baq: BAQDefinition | dict[str, Any],
    conn_str: str | None = None,
    env_var: str = "BAQ_CONNECTION_STRING",
    connection: Any | None = None,
) -> tuple[list[str], list[dict[str, str]]]:
    """Compile and execute a BAQ against SQL Server via pyodbc.

    Returns:
        (columns, rows) where `columns` is the list of result column names and
        `rows` is a list of dicts mapping column name -> formatted string value.
    """
    if isinstance(baq, dict):
        baq = validate_baq(baq)

    sql = compile_baq(baq, include_header=False)

    close_conn = False
    if connection is None:
        resolved_conn_str = get_connection_string(conn_str=conn_str, env_var=env_var)
        try:
            import pyodbc  # type: ignore[import-not-found]
        except ImportError as exc:
            raise BAQRunnerError(
                "pyodbc is required to run BAQ queries against SQL Server, but it is not installed."
            ) from exc

        try:
            connection = pyodbc.connect(resolved_conn_str)
            close_conn = True
        except Exception as exc:
            raise BAQRunnerError(f"Failed to connect to SQL Server via pyodbc: {exc}") from exc

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        if cursor.description is None:
            return [], []
        columns = [col[0] for col in cursor.description]
        raw_rows = cursor.fetchall()
        rows: list[dict[str, str]] = []
        for raw_row in raw_rows:
            row_dict = {
                col: format_cell_value(val)
                for col, val in zip(columns, raw_row)
            }
            rows.append(row_dict)
        return columns, rows
    except Exception as exc:
        raise BAQRunnerError(f"Error executing compiled BAQ SQL: {exc}") from exc
    finally:
        if close_conn and connection is not None:
            try:
                connection.close()
            except Exception:
                pass


def run_baq_file(
    path: str | Path,
    conn_str: str | None = None,
    env_var: str = "BAQ_CONNECTION_STRING",
    connection: Any | None = None,
) -> tuple[list[str], list[dict[str, str]]]:
    """Load a BAQ JSON file, compile it, and execute it via pyodbc."""
    baq = load_baq(path)
    return run_baq(baq, conn_str=conn_str, env_var=env_var, connection=connection)


def rows_to_csv(columns: list[str], rows: list[dict[str, str]]) -> str:
    """Serialize result columns and rows to CSV text."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()
