# BAQ Engine (`engines/baq/`)

JSON Business Activity Query (BAQ) schema, SQL Server 2016 T-SQL compiler targeting `[ErpLab].[Erp].*`, `pyodbc` runner, and CSV result grader.

> **Default chosen for the lab, not confirmed against Epicor.**
> See [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`docs/reference/needs-confirmation.md`](../../docs/reference/needs-confirmation.md) (Approved Defaults 35, 37, 38, 39, 46).

---

## Scope & Supported Designer Features

- **Subquery types**: `TopLevel` and `InnerSubQuery` only (`[B17]`). `CTE`, `RecursiveCTE`, `Union`, `UnionAll`, `Intersect`, `Except`, and `@Parameter` tokens are rejected as out of scope.
- **Tables & Relations**: Three-part `[ErpLab].[Erp].[<Table>]` references (`[B2]`), `inner` and `left` (`left outer`) joins (`[B2]`), and `InnerSubQuery` derived tables (`[B17]`).
- **Display Fields**: Output columns on `TopLevel` follow `<Table>_<Field>` naming (`[B18]`). Supports `groupBy` and aggregate functions (`SUM`, `COUNT`, `MIN`, `MAX`, `AVG`) for subquery aggregation.
- **Calculated Fields (Question 8)**: Written in T-SQL scalar expression syntax (`CASE ... END`, `ISNULL`, `CAST(... AS DECIMAL(7,2))`, `DATEDIFF(day, ...)`, `CONVERT(int, ...)` `[B7-B12]`). Inserted verbatim into the `SELECT` list as `AS [Calculated_<Name>]` (`[B18]`, Approved Default 46). Rejects leading `SELECT` or trailing `AS <alias>` (`[B12]`). `Constants.Today` / `Constants.FixedLabDate` resolves against `[ErpLab].[Erp].[LabConstants]` (`ConstantName = N'FixedLabDate'`, [`sql/00-README.md`](../../sql/00-README.md) §2).
- **Criteria**: Supports both `tableCriteria` (or per-table `criteria`) and `subQueryCriteria` (`[B5, B6]`).

---

## CLI Usage

```bash
# 1. Compile a BAQ JSON file to SQL Server 2016 T-SQL
engines/baq/baq compile engines/baq/examples/open_orders.json

# 2. Run a BAQ against SQL Server (uses $BAQ_CONNECTION_STRING)
export BAQ_CONNECTION_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=ErpLab;UID=sa;PWD=..."
engines/baq/baq run engines/baq/examples/open_orders.json

# 3. Grade a BAQ's results against an expected CSV
engines/baq/baq grade engines/baq/examples/open_orders.json expected.csv
```

---

## Running Unit Tests (No Database Required)

```bash
python3 -m unittest discover -s engines/baq/tests -v
```
