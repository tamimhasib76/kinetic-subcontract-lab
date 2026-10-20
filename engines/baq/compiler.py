"""Compile a validated BAQ definition to SQL Server 2016 T-SQL against [ErpLab].[Erp].*.

Citations & Rules:
- docs/reference/02-baq.md §1.1, §1.3, §1.4 [B17]: TopLevel and InnerSubQuery only.
- docs/reference/02-baq.md §2.2 [B2]: Inner and left outer joins.
- docs/reference/02-baq.md §3.4 [B18]: Output columns named <Table>_<Field> and Calculated_<Name>.
- docs/reference/02-baq.md §4 & Answer 8 [B7-B12]: Calculated fields use T-SQL scalar expressions.
- docs/reference/needs-confirmation.md Approved Default 46 (with banner): Calculated field
  expression text is inserted verbatim into the SELECT list.
- sql/00-README.md §2: Constants.Today / Constants.FixedLabDate resolve against
  [ErpLab].[Erp].[LabConstants] (ConstantName = N'FixedLabDate').
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .schema import (
    BANNER,
    BAQDefinition,
    CalculatedField,
    Criterion,
    DisplayField,
    OrderByItem,
    SubQuery,
    TableEntry,
    load_baq,
    validate_baq,
)

CONSTANTS_TODAY_RE = re.compile(r"\bConstants\.(?:Today|FixedLabDate)\b", re.IGNORECASE)
AGG_FUNC_RE = re.compile(r"\b(?:SUM|COUNT|MIN|MAX|AVG|STRING_AGG)\s*\(", re.IGNORECASE)


class BAQCompilationError(ValueError):
    """Raised when a BAQ definition cannot be compiled to valid T-SQL."""


def quote_ident(ident: str) -> str:
    """Bracket-quote a SQL Server identifier (SQL Server 2016 QUOTENAME style)."""
    return "[" + ident.replace("]", "]]") + "]"


def format_sql_literal(val: Any, database: str = "ErpLab", schema: str = "Erp") -> str:
    """Format a Python literal value as a SQL Server 2016 literal."""
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        if CONSTANTS_TODAY_RE.fullmatch(val.strip()):
            return (
                f"(SELECT [ConstantDate] FROM {quote_ident(database)}.{quote_ident(schema)}.[LabConstants] "
                "WHERE [ConstantName] = N'FixedLabDate')"
            )
        escaped = val.replace("'", "''")
        return f"N'{escaped}'"
    raise BAQCompilationError(f"Unsupported SQL literal value: {val!r}")


def expand_baq_tokens(expr: str, database: str = "ErpLab", schema: str = "Erp") -> str:
    """Replace BAQ constant tokens (Constants.Today / Constants.FixedLabDate) with Erp.LabConstants lookup."""
    replacement = (
        f"(SELECT [ConstantDate] FROM {quote_ident(database)}.{quote_ident(schema)}.[LabConstants] "
        "WHERE [ConstantName] = N'FixedLabDate')"
    )
    return CONSTANTS_TODAY_RE.sub(replacement, expr)


def _compile_criterion(
    crit: Criterion,
    default_table: str | None,
    database: str,
    schema: str,
) -> str:
    if crit.operator == "EXPR" and crit.expression is not None:
        return expand_baq_tokens(crit.expression, database, schema)

    tbl = crit.table or default_table
    if not tbl or not crit.field:
        raise BAQCompilationError("Criterion is missing table or field reference.")

    lhs = f"{quote_ident(tbl)}.{quote_ident(crit.field)}"
    op = crit.operator

    if op in ("IS NULL", "IS NOT NULL"):
        return f"{lhs} {op}"

    if crit.other_table and crit.other_field:
        rhs = f"{quote_ident(crit.other_table)}.{quote_ident(crit.other_field)}"
        return f"{lhs} {op} {rhs}"

    if crit.expression is not None:
        rhs = expand_baq_tokens(crit.expression, database, schema)
        return f"{lhs} {op} {rhs}"

    if op in ("IN", "NOT IN"):
        items = ", ".join(format_sql_literal(v, database, schema) for v in crit.value)
        return f"{lhs} {op} ({items})"

    if op == "BETWEEN":
        low = format_sql_literal(crit.value[0], database, schema)
        high = format_sql_literal(crit.value[1], database, schema)
        return f"{lhs} BETWEEN {low} AND {high}"

    rhs = format_sql_literal(crit.value, database, schema)
    return f"{lhs} {op} {rhs}"


def _combine_criteria(clauses: list[tuple[str, str]]) -> str:
    """Combine (conjunction, sql_predicate) pairs into a WHERE expression."""
    if not clauses:
        return ""
    parts: list[str] = []
    for idx, (conj, pred) in enumerate(clauses):
        if idx == 0:
            parts.append(pred)
        else:
            parts.append(f"{conj} {pred}")
    return "\n  ".join(parts)


def _output_alias_for_display(df: DisplayField, is_top_level: bool) -> str:
    if df.alias:
        return df.alias
    if is_top_level:
        return f"{df.table}_{df.field}"
    return df.field


def _output_alias_for_calc(cf: CalculatedField, is_top_level: bool) -> str:
    if cf.alias:
        return cf.alias
    if is_top_level:
        return f"Calculated_{cf.name}"
    return cf.name


def _compile_subquery(
    sq: SubQuery,
    sq_map: dict[str, SubQuery],
    database: str,
    default_schema: str,
    indent: int = 0,
    call_stack: tuple[str, ...] = (),
) -> str:
    if sq.name in call_stack:
        cycle = " -> ".join((*call_stack, sq.name))
        raise BAQCompilationError(
            f"Circular InnerSubQuery reference detected ({cycle}). Recursive queries / CTEs are out of scope."
        )

    is_top_level = sq.subquery_type == "TopLevel"
    pad = " " * indent
    select_kw = "SELECT DISTINCT" if sq.distinct else "SELECT"

    # Build SELECT list
    select_items: list[str] = []
    group_by_exprs: list[str] = []
    has_aggregates = any(df.aggregate is not None or df.group_by for df in sq.display_fields) or any(
        cf.aggregate or bool(AGG_FUNC_RE.search(cf.expression)) for cf in sq.calculated_fields
    )

    for df in sq.display_fields:
        col_ref = f"{quote_ident(df.table)}.{quote_ident(df.field)}"
        out_alias = _output_alias_for_display(df, is_top_level)
        if df.aggregate:
            expr_sql = f"{df.aggregate}({col_ref})"
        else:
            expr_sql = col_ref
            if has_aggregates or df.group_by:
                group_by_exprs.append(col_ref)
        select_items.append(f"{pad}    {expr_sql} AS {quote_ident(out_alias)}")

    for cf in sq.calculated_fields:
        expanded_expr = expand_baq_tokens(cf.expression, database, default_schema)
        out_alias = _output_alias_for_calc(cf, is_top_level)
        select_items.append(f"{pad}    {expanded_expr} AS {quote_ident(out_alias)}")

    # Build FROM and JOIN clauses
    table_by_alias: dict[str, TableEntry] = {t.alias: t for t in sq.tables}

    def render_table_source(t: TableEntry) -> str:
        if t.is_subquery:
            inner_sq = sq_map[t.table_name]
            inner_sql = _compile_subquery(
                inner_sq,
                sq_map,
                database,
                default_schema,
                indent=indent + 4,
                call_stack=(*call_stack, sq.name),
            )
            return f"(\n{inner_sql}\n{pad}) AS {quote_ident(t.alias)}"
        return f"{quote_ident(database)}.{quote_ident(t.schema_name)}.{quote_ident(t.table_name)} AS {quote_ident(t.alias)}"

    root_table = sq.tables[0]
    from_lines: list[str] = [f"{pad}FROM {render_table_source(root_table)}"]
    joined_aliases: set[str] = {root_table.alias}

    # Process explicit relations in order
    for rel in sq.relations:
        if rel.child_table in joined_aliases and rel.parent_table not in joined_aliases:
            # Allow relations where the newly introduced table was written as parentTable
            target_alias = rel.parent_table
            flip = True
        else:
            target_alias = rel.child_table
            flip = False

        if target_alias not in table_by_alias:
            raise BAQCompilationError(
                f"Relation in subquery '{sq.name}' references unknown table alias '{target_alias}'."
            )

        target_entry = table_by_alias[target_alias]
        on_parts: list[str] = []
        for rf in rel.fields:
            left_cond = f"{quote_ident(rel.parent_table)}.{quote_ident(rf.parent_field)}"
            right_cond = f"{quote_ident(rel.child_table)}.{quote_ident(rf.child_field)}"
            if flip:
                on_parts.append(f"{right_cond} {rf.operator} {left_cond}")
            else:
                on_parts.append(f"{left_cond} {rf.operator} {right_cond}")

        join_cond = f"\n{pad}   AND ".join(on_parts)
        if target_alias not in joined_aliases:
            from_lines.append(
                f"{pad}{rel.join_type} {render_table_source(target_entry)}\n{pad}    ON {join_cond}"
            )
            joined_aliases.add(target_alias)
        else:
            # Additional relation between two already-joined tables: append to the last join or WHERE
            from_lines[-1] += f"\n{pad}   AND {join_cond}"

    # Any remaining tables without a relation are emitted as CROSS JOIN (e.g., Erp.LabConstants)
    for t in sq.tables[1:]:
        if t.alias not in joined_aliases:
            from_lines.append(f"{pad}CROSS JOIN {render_table_source(t)}")
            joined_aliases.add(t.alias)

    # Collect criteria: per-table criteria, subquery table_criteria, and subquery_criteria
    compiled_criteria: list[tuple[str, str]] = []
    for t in sq.tables:
        for crit in t.criteria:
            compiled_criteria.append(
                (crit.conjunction, _compile_criterion(crit, t.alias, database, default_schema))
            )
    for crit in sq.table_criteria:
        default_tbl = sq.tables[0].alias if len(sq.tables) == 1 else None
        compiled_criteria.append(
            (crit.conjunction, _compile_criterion(crit, default_tbl, database, default_schema))
        )
    for crit in sq.subquery_criteria:
        default_tbl = sq.tables[0].alias if len(sq.tables) == 1 else None
        compiled_criteria.append(
            (crit.conjunction, _compile_criterion(crit, default_tbl, database, default_schema))
        )

    lines: list[str] = [f"{pad}{select_kw}", ",\n".join(select_items), *from_lines]

    if compiled_criteria:
        where_body = _combine_criteria(compiled_criteria)
        if indent > 0:
            where_body = where_body.replace("\n  ", f"\n{pad}  ")
        lines.append(f"{pad}WHERE {where_body}")

    if group_by_exprs:
        # Deduplicate while preserving order
        seen_gb: set[str] = set()
        unique_gb: list[str] = []
        for gb in group_by_exprs:
            if gb not in seen_gb:
                seen_gb.add(gb)
                unique_gb.append(gb)
        lines.append(f"{pad}GROUP BY {', '.join(unique_gb)}")

    if sq.order_by and is_top_level:
        ob_parts: list[str] = []
        for ob in sq.order_by:
            ob_parts.append(_format_order_by(ob, sq))
        lines.append(f"{pad}ORDER BY {', '.join(ob_parts)}")

    return "\n".join(lines)


def _format_order_by(ob: OrderByItem, sq: SubQuery) -> str:
    if ob.table:
        return f"{quote_ident(ob.table)}.{quote_ident(ob.field)} {ob.direction}"
    # Check if ob.field matches a calculated field name
    calc_names = {cf.name for cf in sq.calculated_fields}
    if ob.field in calc_names and sq.subquery_type == "TopLevel":
        return f"{quote_ident('Calculated_' + ob.field)} {ob.direction}"
    return f"{quote_ident(ob.field)} {ob.direction}"


def compile_baq(baq: BAQDefinition | dict[str, Any], include_header: bool = True) -> str:
    """Compile a BAQDefinition (or raw BAQ dict) into SQL Server 2016 T-SQL."""
    if isinstance(baq, dict):
        baq = validate_baq(baq)

    sq_map = {sq.name: sq for sq in baq.subqueries}
    top_sq = next(sq for sq in baq.subqueries if sq.subquery_type == "TopLevel")

    body = _compile_subquery(
        top_sq,
        sq_map,
        database=baq.database,
        default_schema=baq.default_schema,
        indent=0,
    )
    sql_stmt = body + ";"

    if not include_header:
        return sql_stmt

    header_lines = [
        f"-- BAQ ID: {baq.baq_id}",
    ]
    if baq.description:
        header_lines.append(f"-- Description: {baq.description}")
    header_lines.append("-- Target: Microsoft SQL Server 2016+ ([ErpLab].[Erp].*)")
    for banner in baq.banners:
        header_lines.append(f"-- Banner: {banner}")
    for citation in baq.citations:
        header_lines.append(f"-- Citation: {citation}")

    return "\n".join(header_lines) + "\n" + sql_stmt


def compile_baq_file(path: str | Path, include_header: bool = True) -> str:
    """Load a BAQ JSON file from disk and compile it to T-SQL."""
    baq = load_baq(path)
    return compile_baq(baq, include_header=include_header)
