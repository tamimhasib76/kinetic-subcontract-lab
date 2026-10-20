"""JSON BAQ definition schema and validator mirroring the BAQ Designer.

Supports:
- Subquery types: TopLevel and InnerSubQuery only (docs/reference/02-baq.md §1.1, §1.3, §1.4 [B17]).
- Rejects CTE, RecursiveCTE, Union, UnionAll, Intersect, Except, and @Parameters (out of scope per
  docs/reference/02-baq.md & docs/reference/needs-confirmation.md Bucket C).
- Tables, table relations (inner / left outer joins [B2]), display fields (<Table>_<Field> [B18]),
  calculated fields in T-SQL expression syntax (Question 8, [B7, B8, B9, B10, B11, B12],
  Approved Default 46), and Table Criteria / SubQuery Criteria ([B5, B6]).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BANNER = "Default chosen for the lab, not confirmed against Epicor."

ALLOWED_SUBQUERY_TYPES = {"TopLevel", "InnerSubQuery"}
FORBIDDEN_SUBQUERY_TYPES = {
    "CTE",
    "RecursiveCTE",
    "Union",
    "UnionAll",
    "Intersect",
    "Except",
}

ALLOWED_JOIN_TYPES = {
    "inner": "INNER JOIN",
    "inner join": "INNER JOIN",
    "innerjoin": "INNER JOIN",
    "left": "LEFT OUTER JOIN",
    "left outer": "LEFT OUTER JOIN",
    "left outer join": "LEFT OUTER JOIN",
    "leftouter": "LEFT OUTER JOIN",
    "leftouterjoin": "LEFT OUTER JOIN",
    "left join": "LEFT OUTER JOIN",
}

ALLOWED_OPERATORS = {
    "=",
    "<>",
    "!=",
    "<",
    "<=",
    ">",
    ">=",
    "LIKE",
    "NOT LIKE",
    "IN",
    "NOT IN",
    "IS NULL",
    "IS NOT NULL",
    "BETWEEN",
}

ALLOWED_AGGREGATES = {"SUM", "COUNT", "MIN", "MAX", "AVG"}

ALLOWED_DATA_TYPES = {
    "int",
    "integer",
    "bigint",
    "decimal",
    "numeric",
    "float",
    "nvarchar",
    "varchar",
    "char",
    "nchar",
    "date",
    "datetime",
    "bit",
}

IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# Parameter token outside single-quoted SQL string literals (@@system variables are not BAQ params)
PARAM_RE = re.compile(r"(?<![A-Za-z0-9_@])@[A-Za-z_][A-Za-z0-9_]*")
LEADING_SELECT_RE = re.compile(r"^\s*SELECT\b", re.IGNORECASE)
# Trailing AS <alias> outside parentheses (02-baq.md §4.7 [B12])
TRAILING_ALIAS_RE = re.compile(r"\bAS\s+(?:\[[A-Za-z_][A-Za-z0-9_]*\]|[A-Za-z_][A-Za-z0-9_]*)\s*$", re.IGNORECASE)


class BAQValidationError(ValueError):
    """Raised when a BAQ JSON definition violates schema or scope rules."""


def _strip_single_quoted_strings(expr: str) -> str:
    """Remove single-quoted literals so @ or keywords inside strings do not trigger false positives."""
    return re.sub(r"N?'(?:''|[^'])*'", "''", expr)


def _has_unparenthesized_trailing_alias(expr: str) -> bool:
    """Check if an expression ends with a top-level `AS <alias>` (invalid per [B12]).

    Note: `CAST(x AS DECIMAL(7,2))` ends with `)`, so it does not match TRAILING_ALIAS_RE,
    while `CAST(x AS INT)` has `AS INT` inside parentheses, not at top level.
    """
    stripped = expr.strip()
    if not TRAILING_ALIAS_RE.search(stripped):
        return False
    # Verify the last `AS` is at parenthesis depth 0
    cleaned = _strip_single_quoted_strings(stripped)
    depth = 0
    last_top_level_as = -1
    i = 0
    n = len(cleaned)
    while i < n:
        ch = cleaned[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and cleaned[i : i + 2].upper() == "AS":
            before_ok = i == 0 or not (cleaned[i - 1].isalnum() or cleaned[i - 1] == "_")
            after_ok = (i + 2 < n) and cleaned[i + 2].isspace()
            if before_ok and after_ok:
                last_top_level_as = i
        i += 1
    if last_top_level_as == -1:
        return False
    tail = cleaned[last_top_level_as:]
    return bool(re.match(r"^AS\s+(?:\[[A-Za-z_][A-Za-z0-9_]*\]|[A-Za-z_][A-Za-z0-9_]*)\s*$", tail, re.IGNORECASE))


def validate_identifier(name: str, context: str) -> str:
    if not isinstance(name, str) or not IDENT_RE.match(name):
        raise BAQValidationError(f"Invalid identifier {name!r} in {context}.")
    return name


def check_no_parameters(text: str, context: str) -> None:
    cleaned = _strip_single_quoted_strings(text)
    m = PARAM_RE.search(cleaned)
    if m:
        raise BAQValidationError(
            f"BAQ parameters ({m.group(0)}) in {context} are not supported in Phase 2b "
            "(docs/reference/02-baq.md §5.2; needs-confirmation.md Bucket C)."
        )


@dataclass
class Criterion:
    table: str | None
    field: str | None
    operator: str
    value: Any = None
    other_table: str | None = None
    other_field: str | None = None
    expression: str | None = None
    conjunction: str = "AND"


@dataclass
class TableEntry:
    table_name: str
    alias: str
    schema_name: str = "Erp"
    is_subquery: bool = False
    criteria: list[Criterion] = field(default_factory=list)


@dataclass
class RelationField:
    parent_field: str
    child_field: str
    operator: str = "="


@dataclass
class Relation:
    parent_table: str
    child_table: str
    join_type: str  # Normalized to "INNER JOIN" or "LEFT OUTER JOIN"
    fields: list[RelationField]
    name: str | None = None


@dataclass
class DisplayField:
    table: str
    field: str
    alias: str | None = None
    group_by: bool = False
    aggregate: str | None = None


@dataclass
class CalculatedField:
    name: str
    data_type: str
    expression: str
    alias: str | None = None
    aggregate: bool = False


@dataclass
class OrderByItem:
    table: str | None
    field: str
    direction: str = "ASC"


@dataclass
class SubQuery:
    name: str
    subquery_type: str  # "TopLevel" or "InnerSubQuery"
    tables: list[TableEntry]
    relations: list[Relation] = field(default_factory=list)
    display_fields: list[DisplayField] = field(default_factory=list)
    calculated_fields: list[CalculatedField] = field(default_factory=list)
    table_criteria: list[Criterion] = field(default_factory=list)
    subquery_criteria: list[Criterion] = field(default_factory=list)
    order_by: list[OrderByItem] = field(default_factory=list)
    distinct: bool = False


@dataclass
class BAQDefinition:
    baq_id: str
    description: str
    subqueries: list[SubQuery]
    database: str = "ErpLab"
    default_schema: str = "Erp"
    citations: list[str] = field(default_factory=list)
    banners: list[str] = field(default_factory=list)


def _parse_criterion(raw: dict[str, Any], default_table: str | None, context: str) -> Criterion:
    if not isinstance(raw, dict):
        raise BAQValidationError(f"Criterion in {context} must be a JSON object.")

    conjunction = str(raw.get("conjunction", raw.get("andOr", "AND"))).strip().upper()
    if conjunction not in ("AND", "OR"):
        raise BAQValidationError(f"Invalid criterion conjunction {conjunction!r} in {context}; use 'AND' or 'OR'.")

    if "expression" in raw and raw["expression"] is not None and "field" not in raw:
        expr = str(raw["expression"]).strip()
        if not expr:
            raise BAQValidationError(f"Empty criterion expression in {context}.")
        check_no_parameters(expr, context)
        return Criterion(
            table=default_table,
            field=None,
            operator="EXPR",
            expression=expr,
            conjunction=conjunction,
        )

    table = raw.get("table", default_table)
    if table is not None:
        validate_identifier(str(table), f"{context}.table")
    field_name = raw.get("field", raw.get("column"))
    validate_identifier(str(field_name), f"{context}.field")

    op_raw = str(raw.get("operator", "=")).strip().upper()
    op_raw = " ".join(op_raw.split())
    if op_raw == "!=":
        op_raw = "<>"
    if op_raw not in ALLOWED_OPERATORS:
        raise BAQValidationError(
            f"Unsupported operator {op_raw!r} in {context}. Allowed: {', '.join(sorted(ALLOWED_OPERATORS))}."
        )

    other_table = raw.get("otherTable", raw.get("compareTable"))
    other_field = raw.get("otherField", raw.get("compareField"))
    if other_table is not None or other_field is not None:
        if not other_table or not other_field:
            raise BAQValidationError(f"{context} column comparison requires both otherTable and otherField.")
        validate_identifier(str(other_table), f"{context}.otherTable")
        validate_identifier(str(other_field), f"{context}.otherField")

    expr = raw.get("expression", raw.get("sqlExpression"))
    if expr is not None:
        expr = str(expr).strip()
        check_no_parameters(expr, f"{context}.expression")

    value = raw.get("value")
    if isinstance(value, str):
        check_no_parameters(value, f"{context}.value")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                check_no_parameters(item, f"{context}.value")

    if op_raw in ("IS NULL", "IS NOT NULL"):
        pass
    elif op_raw in ("IN", "NOT IN"):
        if not isinstance(value, list) or len(value) == 0:
            raise BAQValidationError(f"{context} with operator {op_raw} requires a non-empty list in 'value'.")
    elif op_raw == "BETWEEN":
        if not isinstance(value, list) or len(value) != 2:
            raise BAQValidationError(f"{context} with operator BETWEEN requires a 2-element list in 'value'.")
    elif other_table is None and expr is None and "value" not in raw:
        raise BAQValidationError(
            f"{context} requires 'value', 'expression', or ('otherTable' and 'otherField')."
        )

    return Criterion(
        table=str(table) if table else None,
        field=str(field_name),
        operator=op_raw,
        value=value,
        other_table=str(other_table) if other_table else None,
        other_field=str(other_field) if other_field else None,
        expression=expr,
        conjunction=conjunction,
    )


def _parse_subquery(raw: dict[str, Any], index: int, default_schema: str) -> SubQuery:
    ctx = f"subqueries[{index}]"
    if not isinstance(raw, dict):
        raise BAQValidationError(f"{ctx} must be a JSON object.")

    name = validate_identifier(str(raw.get("name", raw.get("subQueryName", f"SubQuery{index + 1}"))), f"{ctx}.name")
    sq_type = str(raw.get("type", raw.get("subQueryType", "TopLevel"))).strip()

    for forbidden in FORBIDDEN_SUBQUERY_TYPES:
        if sq_type.lower() == forbidden.lower():
            raise BAQValidationError(
                f"Subquery '{name}' has type '{sq_type}', which is not supported. "
                "Only 'TopLevel' and 'InnerSubQuery' are allowed (no CTE, Union, or UnionAll)."
            )
    if sq_type not in ALLOWED_SUBQUERY_TYPES:
        raise BAQValidationError(
            f"Subquery '{name}' has invalid type {sq_type!r}. Allowed: TopLevel, InnerSubQuery."
        )

    raw_tables = raw.get("tables", [])
    if not isinstance(raw_tables, list) or not raw_tables:
        raise BAQValidationError(f"Subquery '{name}' must define a non-empty 'tables' list.")

    tables: list[TableEntry] = []
    seen_aliases: set[str] = set()
    for t_idx, t_raw in enumerate(raw_tables):
        t_ctx = f"{ctx}.tables[{t_idx}]"
        if isinstance(t_raw, str):
            t_name = validate_identifier(t_raw, t_ctx)
            t_alias = t_name
            t_schema = default_schema
            is_sq = False
            t_crit: list[Criterion] = []
        elif isinstance(t_raw, dict):
            t_name = validate_identifier(
                str(t_raw.get("table", t_raw.get("tableName", t_raw.get("name", "")))),
                f"{t_ctx}.table",
            )
            t_alias = validate_identifier(
                str(t_raw.get("alias", t_name)),
                f"{t_ctx}.alias",
            )
            t_schema = validate_identifier(
                str(t_raw.get("schema", t_raw.get("schemaName", default_schema))),
                f"{t_ctx}.schema",
            )
            is_sq = bool(t_raw.get("isSubQuery", t_raw.get("subQuery", False)))
            t_crit = [
                _parse_criterion(c, t_alias, f"{t_ctx}.criteria[{c_i}]")
                for c_i, c in enumerate(t_raw.get("criteria", []))
            ]
        else:
            raise BAQValidationError(f"{t_ctx} must be an object or table name string.")

        if t_alias in seen_aliases:
            raise BAQValidationError(f"Duplicate table alias '{t_alias}' in subquery '{name}'.")
        seen_aliases.add(t_alias)
        tables.append(
            TableEntry(
                table_name=t_name,
                alias=t_alias,
                schema_name=t_schema,
                is_subquery=is_sq,
                criteria=t_crit,
            )
        )

    raw_relations = raw.get("relations", raw.get("relationships", []))
    relations: list[Relation] = []
    for r_idx, r_raw in enumerate(raw_relations):
        r_ctx = f"{ctx}.relations[{r_idx}]"
        if not isinstance(r_raw, dict):
            raise BAQValidationError(f"{r_ctx} must be a JSON object.")
        parent = validate_identifier(
            str(r_raw.get("parentTable", r_raw.get("parent", r_raw.get("fromTable", "")))),
            f"{r_ctx}.parentTable",
        )
        child = validate_identifier(
            str(r_raw.get("childTable", r_raw.get("child", r_raw.get("toTable", "")))),
            f"{r_ctx}.childTable",
        )
        jt_raw = str(r_raw.get("joinType", r_raw.get("type", "inner"))).strip().lower()
        jt_raw = " ".join(jt_raw.split())
        if jt_raw not in ALLOWED_JOIN_TYPES:
            raise BAQValidationError(
                f"Unsupported joinType {r_raw.get('joinType')!r} in {r_ctx}. "
                "BAQ supports 'inner' and 'left' ('left outer') joins [B2]."
            )
        raw_fields = r_raw.get("fields", r_raw.get("on", []))
        if not isinstance(raw_fields, list) or not raw_fields:
            raise BAQValidationError(f"Relation {r_ctx} between '{parent}' and '{child}' must specify join 'fields'.")
        rel_fields: list[RelationField] = []
        for f_idx, f_raw in enumerate(raw_fields):
            f_ctx = f"{r_ctx}.fields[{f_idx}]"
            p_field = validate_identifier(
                str(f_raw.get("parentField", f_raw.get("parent", f_raw.get("fromField", "")))),
                f"{f_ctx}.parentField",
            )
            c_field = validate_identifier(
                str(f_raw.get("childField", f_raw.get("child", f_raw.get("toField", "")))),
                f"{f_ctx}.childField",
            )
            op = str(f_raw.get("operator", "=")).strip()
            if op not in ("=", "<>", "<", "<=", ">", ">="):
                raise BAQValidationError(f"Invalid join operator {op!r} in {f_ctx}.")
            rel_fields.append(RelationField(parent_field=p_field, child_field=c_field, operator=op))
        relations.append(
            Relation(
                parent_table=parent,
                child_table=child,
                join_type=ALLOWED_JOIN_TYPES[jt_raw],
                fields=rel_fields,
                name=r_raw.get("name", r_raw.get("relationshipName")),
            )
        )

    display_fields: list[DisplayField] = []
    for d_idx, d_raw in enumerate(raw.get("displayFields", [])):
        d_ctx = f"{ctx}.displayFields[{d_idx}]"
        if not isinstance(d_raw, dict):
            raise BAQValidationError(f"{d_ctx} must be a JSON object.")
        d_table = validate_identifier(str(d_raw.get("table", "")), f"{d_ctx}.table")
        d_field = validate_identifier(str(d_raw.get("field", d_raw.get("column", ""))), f"{d_ctx}.field")
        d_alias = d_raw.get("alias")
        if d_alias is not None:
            validate_identifier(str(d_alias), f"{d_ctx}.alias")
        d_agg = d_raw.get("aggregate")
        if d_agg is not None:
            d_agg = str(d_agg).strip().upper()
            if d_agg not in ALLOWED_AGGREGATES:
                raise BAQValidationError(
                    f"Unsupported aggregate {d_agg!r} in {d_ctx}. Allowed: {', '.join(sorted(ALLOWED_AGGREGATES))}."
                )
        display_fields.append(
            DisplayField(
                table=d_table,
                field=d_field,
                alias=str(d_alias) if d_alias else None,
                group_by=bool(d_raw.get("groupBy", False)),
                aggregate=d_agg,
            )
        )

    calculated_fields: list[CalculatedField] = []
    seen_calc: set[str] = set()
    for c_idx, c_raw in enumerate(raw.get("calculatedFields", [])):
        c_ctx = f"{ctx}.calculatedFields[{c_idx}]"
        if not isinstance(c_raw, dict):
            raise BAQValidationError(f"{c_ctx} must be a JSON object.")
        c_name = validate_identifier(str(c_raw.get("name", "")), f"{c_ctx}.name")
        if c_name.startswith("Calculated_"):
            c_name = c_name[len("Calculated_") :]
            validate_identifier(c_name, f"{c_ctx}.name")
        if c_name in seen_calc:
            raise BAQValidationError(f"Duplicate calculated field '{c_name}' in subquery '{name}'.")
        seen_calc.add(c_name)

        c_dtype = str(c_raw.get("dataType", "nvarchar")).strip().lower()
        base_dtype = c_dtype.split("(")[0].strip()
        if base_dtype not in ALLOWED_DATA_TYPES:
            raise BAQValidationError(
                f"Unsupported dataType {c_dtype!r} on calculated field '{c_name}' in {c_ctx}."
            )

        expr = str(c_raw.get("expression", "")).strip()
        if not expr:
            raise BAQValidationError(f"Calculated field '{c_name}' in {c_ctx} has an empty expression.")
        check_no_parameters(expr, f"{c_ctx} ('{c_name}')")
        if LEADING_SELECT_RE.search(expr):
            raise BAQValidationError(
                f"Calculated field '{c_name}' in {c_ctx} must not start with SELECT; "
                "enter only the scalar T-SQL expression (docs/reference/02-baq.md §4.7, Answer 8 [B12])."
            )
        if _has_unparenthesized_trailing_alias(expr):
            raise BAQValidationError(
                f"Calculated field '{c_name}' in {c_ctx} must not end with 'AS <alias>'; "
                "enter only the expression (docs/reference/02-baq.md §4.7 [B12])."
            )

        c_alias = c_raw.get("alias")
        if c_alias is not None:
            validate_identifier(str(c_alias), f"{c_ctx}.alias")

        calculated_fields.append(
            CalculatedField(
                name=c_name,
                data_type=c_dtype,
                expression=expr,
                alias=str(c_alias) if c_alias else None,
                aggregate=bool(c_raw.get("aggregate", c_raw.get("isAggregate", False))),
            )
        )

    if not display_fields and not calculated_fields:
        raise BAQValidationError(
            f"Subquery '{name}' must define at least one displayField or calculatedField."
        )

    table_criteria = [
        _parse_criterion(c, None, f"{ctx}.tableCriteria[{i}]")
        for i, c in enumerate(raw.get("tableCriteria", []))
    ]
    subquery_criteria = [
        _parse_criterion(c, None, f"{ctx}.criteria[{i}]")
        for i, c in enumerate(raw.get("subQueryCriteria", raw.get("criteria", [])))
    ]

    order_by: list[OrderByItem] = []
    for o_idx, o_raw in enumerate(raw.get("orderBy", raw.get("sort", []))):
        o_ctx = f"{ctx}.orderBy[{o_idx}]"
        if not isinstance(o_raw, dict):
            raise BAQValidationError(f"{o_ctx} must be a JSON object.")
        o_table = o_raw.get("table")
        if o_table is not None:
            validate_identifier(str(o_table), f"{o_ctx}.table")
        o_field = validate_identifier(str(o_raw.get("field", o_raw.get("column", ""))), f"{o_ctx}.field")
        direction = str(o_raw.get("direction", "ASC")).strip().upper()
        if direction not in ("ASC", "DESC"):
            raise BAQValidationError(f"Invalid sort direction {direction!r} in {o_ctx}; use 'ASC' or 'DESC'.")
        order_by.append(
            OrderByItem(
                table=str(o_table) if o_table else None,
                field=o_field,
                direction=direction,
            )
        )

    return SubQuery(
        name=name,
        subquery_type=sq_type,
        tables=tables,
        relations=relations,
        display_fields=display_fields,
        calculated_fields=calculated_fields,
        table_criteria=table_criteria,
        subquery_criteria=subquery_criteria,
        order_by=order_by,
        distinct=bool(raw.get("distinct", False)),
    )


SCHEMA_SQL_CREATE_RE = re.compile(
    r"CREATE\s+TABLE\s+Erp\.([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\);",
    re.DOTALL | re.IGNORECASE,
)
QUALIFIED_COL_RE = re.compile(
    r"(?:\[(?P<q_tbl>[A-Za-z_][A-Za-z0-9_]*)\]|(?P<u_tbl>[A-Za-z_][A-Za-z0-9_]*))"
    r"\s*\.\s*"
    r"(?:\[(?P<q_col>[A-Za-z_][A-Za-z0-9_]*)\]|(?P<u_col>[A-Za-z_][A-Za-z0-9_]*))"
)
BRACKET_IDENT_RE = re.compile(r"\[([A-Za-z_][A-Za-z0-9_]*)\]")
BARE_IDENT_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b(?!\s*\()")

SQL_RESERVED_TOKENS = {
    # Keywords & operators
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    "AND",
    "OR",
    "NOT",
    "IS",
    "NULL",
    "IN",
    "BETWEEN",
    "LIKE",
    "ESCAPE",
    "AS",
    "DISTINCT",
    "OVER",
    "PARTITION",
    "BY",
    "ORDER",
    "ASC",
    "DESC",
    "TRUE",
    "FALSE",
    # SQL Server data types
    "INT",
    "INTEGER",
    "BIGINT",
    "SMALLINT",
    "TINYINT",
    "BIT",
    "DECIMAL",
    "DEC",
    "NUMERIC",
    "FLOAT",
    "REAL",
    "MONEY",
    "SMALLMONEY",
    "DATE",
    "DATETIME",
    "DATETIME2",
    "SMALLDATETIME",
    "TIME",
    "CHAR",
    "VARCHAR",
    "NCHAR",
    "NVARCHAR",
    "TEXT",
    "NTEXT",
    "BINARY",
    "VARBINARY",
    "UNIQUEIDENTIFIER",
    # Dateparts for DATEDIFF / DATEADD / DATEPART
    "YEAR",
    "YY",
    "YYYY",
    "QUARTER",
    "QQ",
    "Q",
    "MONTH",
    "MM",
    "M",
    "DAYOFYEAR",
    "DY",
    "Y",
    "DAY",
    "DAYS",
    "DD",
    "D",
    "WEEK",
    "WK",
    "WW",
    "WEEKDAY",
    "DW",
    "W",
    "HOUR",
    "HH",
    "MINUTE",
    "MI",
    "N",
    "SECOND",
    "SS",
    "S",
    "MILLISECOND",
    "MS",
    "MICROSECOND",
    "MCS",
    "NANOSECOND",
    "NS",
}

_CACHED_ERP_SCHEMA: dict[str, set[str]] | None = None


def parse_schema_sql(sql_path: str | Path) -> dict[str, list[str]]:
    """Parse table and column definitions from sql/01-erp-app-schema.sql."""
    text = Path(sql_path).read_text(encoding="utf-8")
    tables: dict[str, list[str]] = {}
    for m in SCHEMA_SQL_CREATE_RE.finditer(text):
        table_name = m.group(1)
        body = m.group(2)
        cols: list[str] = []
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("--") or line.upper().startswith("CONSTRAINT"):
                continue
            col_m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s+", line)
            if col_m:
                cols.append(col_m.group(1))
        tables[table_name] = cols
    return tables


def load_erp_schema() -> dict[str, set[str]]:
    """Load [ErpLab].[Erp] table and column names from sql/01-erp-app-schema.sql or engines/baq/schema-tables.json."""
    global _CACHED_ERP_SCHEMA
    if _CACHED_ERP_SCHEMA is not None:
        return _CACHED_ERP_SCHEMA

    here = Path(__file__).resolve().parent
    sql_path = here.parents[1] / "sql" / "01-erp-app-schema.sql"
    json_path = here / "schema-tables.json"

    if sql_path.exists():
        raw_tables = parse_schema_sql(sql_path)
    elif json_path.exists():
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        raw_tables = payload.get("tables", {})
    else:
        raise BAQValidationError(
            f"Cannot locate schema definition at {sql_path} or {json_path}."
        )

    _CACHED_ERP_SCHEMA = {tbl: set(cols) for tbl, cols in raw_tables.items()}
    return _CACHED_ERP_SCHEMA


def _validate_expression_columns(
    expr: str,
    available_cols: dict[str, set[str]],
    alias_map: dict[str, TableEntry],
    calc_names: set[str],
    context: str,
) -> None:
    """Validate that every table/column referenced in a SQL scalar expression exists in [ErpLab].[Erp]."""
    cleaned = _strip_single_quoted_strings(expr)

    # 1. Validate all qualified Alias.Column or [Alias].[Column] references
    for m in QUALIFIED_COL_RE.finditer(cleaned):
        tbl = m.group("q_tbl") or m.group("u_tbl")
        col = m.group("q_col") or m.group("u_col")
        if tbl.lower() == "constants":
            if col.lower() not in ("today", "fixedlabdate"):
                raise BAQValidationError(
                    f"Unknown BAQ constant 'Constants.{col}' in {context}."
                )
            continue
        if tbl not in available_cols:
            raise BAQValidationError(
                f"Expression in {context} references unknown table or alias '{tbl}'."
            )
        if col not in available_cols[tbl]:
            src_name = alias_map[tbl].table_name
            raise BAQValidationError(
                f"Column '{col}' referenced in {context} does not exist on '{src_name}' (alias '{tbl}') in [ErpLab].[Erp]."
            )

    # Remove qualified pairs so we can inspect remaining standalone column identifiers
    remainder = QUALIFIED_COL_RE.sub(" ", cleaned)
    all_valid_cols: set[str] = set(calc_names)
    for cols in available_cols.values():
        all_valid_cols.update(cols)

    # 2. Validate any remaining bracketed identifiers [Col]
    for m in BRACKET_IDENT_RE.finditer(remainder):
        ident = m.group(1)
        if ident.upper() in SQL_RESERVED_TOKENS:
            continue
        if ident not in all_valid_cols:
            raise BAQValidationError(
                f"Column '[{ident}]' referenced in {context} does not exist in [ErpLab].[Erp]."
            )

    # Remove bracketed identifiers and check any remaining bare identifiers
    remainder = BRACKET_IDENT_RE.sub(" ", remainder)
    for m in BARE_IDENT_RE.finditer(remainder):
        ident = m.group(1)
        if ident.upper() in SQL_RESERVED_TOKENS:
            continue
        if ident not in all_valid_cols:
            raise BAQValidationError(
                f"Column '{ident}' referenced in {context} does not exist in [ErpLab].[Erp]."
            )


def validate_baq(data: dict[str, Any]) -> BAQDefinition:
    """Validate a raw BAQ JSON dict and return a structured BAQDefinition."""
    if not isinstance(data, dict):
        raise BAQValidationError("BAQ definition root must be a JSON object.")

    if "parameters" in data and data["parameters"]:
        raise BAQValidationError(
            "BAQ parameters are not supported in Phase 2b (docs/reference/02-baq.md §5.2; "
            "needs-confirmation.md Bucket C)."
        )

    baq_id = validate_identifier(
        str(data.get("baqId", data.get("id", data.get("name", "BAQ")))),
        "baqId",
    )
    description = str(data.get("description", "")).strip()
    database = validate_identifier(str(data.get("database", "ErpLab")), "database")
    default_schema = validate_identifier(str(data.get("schema", "Erp")), "schema")

    if database != "ErpLab":
        raise BAQValidationError(
            f"Unsupported database '{database}' in BAQ '{baq_id}'; only '[ErpLab]' is supported."
        )
    if default_schema != "Erp":
        raise BAQValidationError(
            f"Unsupported schema '{default_schema}' in BAQ '{baq_id}'; only '[ErpLab].[Erp]' is supported."
        )

    # Allow shorthand top-level format where tables/displayFields sit at root
    raw_subqueries = data.get("subqueries", data.get("subQueries"))
    if raw_subqueries is None:
        if "tables" in data:
            raw_subqueries = [
                {
                    "name": data.get("subQueryName", "TopLevel"),
                    "type": data.get("type", "TopLevel"),
                    "tables": data["tables"],
                    "relations": data.get("relations", data.get("relationships", [])),
                    "displayFields": data.get("displayFields", []),
                    "calculatedFields": data.get("calculatedFields", []),
                    "tableCriteria": data.get("tableCriteria", []),
                    "subQueryCriteria": data.get("subQueryCriteria", data.get("criteria", [])),
                    "orderBy": data.get("orderBy", data.get("sort", [])),
                    "distinct": data.get("distinct", False),
                }
            ]
        else:
            raise BAQValidationError("BAQ definition must contain 'subqueries' (or top-level 'tables').")

    if not isinstance(raw_subqueries, list) or not raw_subqueries:
        raise BAQValidationError("BAQ 'subqueries' must be a non-empty list.")

    subqueries = [_parse_subquery(sq, idx, default_schema) for idx, sq in enumerate(raw_subqueries)]

    top_level_sqs = [sq for sq in subqueries if sq.subquery_type == "TopLevel"]
    if len(top_level_sqs) != 1:
        raise BAQValidationError(
            f"BAQ '{baq_id}' must have exactly 1 'TopLevel' subquery (found {len(top_level_sqs)})."
        )

    sq_by_name: dict[str, SubQuery] = {}
    for sq in subqueries:
        if sq.name in sq_by_name:
            raise BAQValidationError(f"Duplicate subquery name '{sq.name}' in BAQ '{baq_id}'.")
        sq_by_name[sq.name] = sq

    erp_schema = load_erp_schema()

    # Compute output column names of each InnerSubQuery
    sq_output_cols: dict[str, set[str]] = {}
    for sq in subqueries:
        if sq.subquery_type == "InnerSubQuery":
            out_cols: set[str] = set()
            for df in sq.display_fields:
                out_cols.add(df.alias if df.alias else df.field)
            for cf in sq.calculated_fields:
                out_cols.add(cf.alias if cf.alias else cf.name)
            sq_output_cols[sq.name] = out_cols

    # Mark tables that reference an InnerSubQuery and validate all table and column references against [ErpLab].[Erp]
    for sq in subqueries:
        alias_map = {t.alias: t for t in sq.tables}
        available_cols: dict[str, set[str]] = {}
        for t in sq.tables:
            if t.table_name in sq_by_name:
                target_sq = sq_by_name[t.table_name]
                if target_sq.subquery_type != "InnerSubQuery":
                    raise BAQValidationError(
                        f"Subquery '{sq.name}' references subquery '{t.table_name}', "
                        f"which has type '{target_sq.subquery_type}' (must be 'InnerSubQuery')."
                    )
                t.is_subquery = True
                available_cols[t.alias] = sq_output_cols[t.table_name]
            elif t.is_subquery:
                raise BAQValidationError(
                    f"Table '{t.table_name}' in subquery '{sq.name}' is marked isSubQuery=true, "
                    f"but no InnerSubQuery named '{t.table_name}' exists."
                )
            else:
                if t.schema_name != "Erp":
                    raise BAQValidationError(
                        f"Table '{t.schema_name}.{t.table_name}' in subquery '{sq.name}' uses schema "
                        f"'{t.schema_name}'; only '[ErpLab].[Erp]' is supported."
                    )
                if t.table_name not in erp_schema:
                    raise BAQValidationError(
                        f"Table '[ErpLab].[Erp].[{t.table_name}]' in subquery '{sq.name}' does not exist in [ErpLab].[Erp]."
                    )
                available_cols[t.alias] = erp_schema[t.table_name]

        # Validate relations reference tables and existing columns in this subquery
        for rel in sq.relations:
            if rel.parent_table not in alias_map:
                raise BAQValidationError(
                    f"Relation in subquery '{sq.name}' references unknown parentTable '{rel.parent_table}'."
                )
            if rel.child_table not in alias_map:
                raise BAQValidationError(
                    f"Relation in subquery '{sq.name}' references unknown childTable '{rel.child_table}'."
                )
            for rf in rel.fields:
                if rf.parent_field not in available_cols[rel.parent_table]:
                    p_src = alias_map[rel.parent_table].table_name
                    raise BAQValidationError(
                        f"Join parentField '{rel.parent_table}.{rf.parent_field}' in subquery '{sq.name}' "
                        f"does not exist on '{p_src}' in [ErpLab].[Erp]."
                    )
                if rf.child_field not in available_cols[rel.child_table]:
                    c_src = alias_map[rel.child_table].table_name
                    raise BAQValidationError(
                        f"Join childField '{rel.child_table}.{rf.child_field}' in subquery '{sq.name}' "
                        f"does not exist on '{c_src}' in [ErpLab].[Erp]."
                    )

        # Validate display fields reference tables and existing columns in this subquery
        for df in sq.display_fields:
            if df.table not in alias_map:
                raise BAQValidationError(
                    f"Display field '{df.table}.{df.field}' in subquery '{sq.name}' "
                    f"references unknown table alias '{df.table}'."
                )
            if df.field not in available_cols[df.table]:
                src_tbl = alias_map[df.table].table_name
                raise BAQValidationError(
                    f"Display field '{df.table}.{df.field}' in subquery '{sq.name}' "
                    f"does not exist on '{src_tbl}' in [ErpLab].[Erp]."
                )

        calc_names = {cf.name for cf in sq.calculated_fields} | {
            cf.alias for cf in sq.calculated_fields if cf.alias
        }

        # Validate calculated field expressions
        for cf in sq.calculated_fields:
            _validate_expression_columns(
                cf.expression,
                available_cols,
                alias_map,
                calc_names,
                f"subquery '{sq.name}' calculatedField '{cf.name}'",
            )

        # Validate criteria (per-table criteria, tableCriteria, and subQueryCriteria)
        all_crit_with_default: list[tuple[Criterion, str | None]] = []
        for t in sq.tables:
            for crit in t.criteria:
                all_crit_with_default.append((crit, t.alias))
        default_sq_tbl = sq.tables[0].alias if len(sq.tables) == 1 else None
        for crit in sq.table_criteria + sq.subquery_criteria:
            all_crit_with_default.append((crit, default_sq_tbl))

        for crit, def_tbl in all_crit_with_default:
            eff_tbl = crit.table or def_tbl
            if crit.field is not None:
                if not eff_tbl or eff_tbl not in alias_map:
                    raise BAQValidationError(
                        f"Criterion on '{crit.table}.{crit.field}' in subquery '{sq.name}' "
                        f"references unknown table alias '{crit.table}'."
                    )
                if crit.field not in available_cols[eff_tbl]:
                    src_tbl = alias_map[eff_tbl].table_name
                    raise BAQValidationError(
                        f"Criterion column '{eff_tbl}.{crit.field}' in subquery '{sq.name}' "
                        f"does not exist on '{src_tbl}' in [ErpLab].[Erp]."
                    )
            if crit.other_table and crit.other_field:
                if crit.other_table not in alias_map:
                    raise BAQValidationError(
                        f"Criterion comparison to '{crit.other_table}.{crit.other_field}' in subquery '{sq.name}' "
                        f"references unknown table alias '{crit.other_table}'."
                    )
                if crit.other_field not in available_cols[crit.other_table]:
                    other_src = alias_map[crit.other_table].table_name
                    raise BAQValidationError(
                        f"Criterion comparison column '{crit.other_table}.{crit.other_field}' in subquery '{sq.name}' "
                        f"does not exist on '{other_src}' in [ErpLab].[Erp]."
                    )
            if crit.expression is not None:
                _validate_expression_columns(
                    crit.expression,
                    available_cols,
                    alias_map,
                    calc_names,
                    f"subquery '{sq.name}' criterion expression",
                )

        # Validate orderBy columns
        display_output_aliases = set()
        for df in sq.display_fields:
            if df.alias:
                display_output_aliases.add(df.alias)
            display_output_aliases.add(f"{df.table}_{df.field}")
            display_output_aliases.add(df.field)
        calc_output_aliases = set(calc_names) | {f"Calculated_{cf.name}" for cf in sq.calculated_fields}

        for ob in sq.order_by:
            if ob.table is not None:
                if ob.table not in alias_map:
                    raise BAQValidationError(
                        f"OrderBy '{ob.table}.{ob.field}' in subquery '{sq.name}' "
                        f"references unknown table alias '{ob.table}'."
                    )
                if ob.field not in available_cols[ob.table]:
                    src_tbl = alias_map[ob.table].table_name
                    raise BAQValidationError(
                        f"OrderBy column '{ob.table}.{ob.field}' in subquery '{sq.name}' "
                        f"does not exist on '{src_tbl}' in [ErpLab].[Erp]."
                    )
            else:
                allowed_unqualified = display_output_aliases | calc_output_aliases
                if len(sq.tables) == 1:
                    allowed_unqualified |= available_cols[sq.tables[0].alias]
                if ob.field not in allowed_unqualified:
                    raise BAQValidationError(
                        f"OrderBy column '{ob.field}' in subquery '{sq.name}' does not exist in [ErpLab].[Erp]."
                    )

    citations = [str(c) for c in data.get("citations", [])]
    banners = [str(b) for b in data.get("banners", [])]
    if BANNER not in banners:
        banners.insert(0, BANNER)

    return BAQDefinition(
        baq_id=baq_id,
        description=description,
        subqueries=subqueries,
        database=database,
        default_schema=default_schema,
        citations=citations,
        banners=banners,
    )


def load_baq(path: str | Path) -> BAQDefinition:
    """Load and validate a BAQ JSON file from disk."""
    p = Path(path)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BAQValidationError(f"Invalid JSON in {p}: {exc}") from exc
    return validate_baq(raw)

