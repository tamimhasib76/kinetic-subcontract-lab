# Lab B10: Order Line Extended Amount (`CAST` to `DECIMAL(15,2)`) (Calculated Fields)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-210` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B10_LineExtendedPrice` |
| **Category** | Build Drill — Calculated Fields |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B10.json`](starter/B10.json) |
| **Summary** | Sales Analytics at MFG01 requests a BAQ (`BAQ_B10_LineExtendedPrice`) on `Erp.OrderDtl` for orders `10061` through `10065` in `MFG01` with a calculated field `LineTotal` (`Calculated_LineTotal`) equal to `CAST([OrderDtl].[OrderQty] * [OrderDtl].[UnitPrice] AS DECIMAL(15,2))`. |

### Acceptance Criteria
1. Query `Erp.OrderDtl` filtered to `Company = 'MFG01'` and `OrderNum BETWEEN 10061 AND 10065`.
2. Include display fields: `OrderDtl.Company`, `OrderDtl.OrderNum`, `OrderDtl.OrderLine`, `OrderDtl.PartNum`, `OrderDtl.OrderQty`, `OrderDtl.UnitPrice` (`[B18]`).
3. Add calculated field `LineTotal` (`dataType: 'decimal'`) with T-SQL expression `CAST([OrderDtl].[OrderQty] * [OrderDtl].[UnitPrice] AS DECIMAL(15,2))` (`[B9, B12, B18]`, Approved Default 46).
4. Sort results by `OrderDtl.OrderNum ASC`, `OrderDtl.OrderLine ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B10.json /tmp/B10.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B10.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B10.json
```
