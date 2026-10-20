# Lab B14: Part Master with Warehouse On-Hand Rollup (`InnerSubQuery`) (InnerSubQuery)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-214` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B14_PartOnHandSummary` |
| **Category** | Build Drill — InnerSubQuery |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B14.json`](starter/B14.json) |
| **Summary** | Inventory Control at MFG01 needs a BAQ (`BAQ_B14_PartOnHandSummary`) that rolls up `Erp.PartWhse` in an `InnerSubQuery` (`WhseSum`) by `Company` and `PartNum` to compute `WarehouseCount` (`COUNT(WarehouseCode)`) and `TotalOnHandQty` (`SUM(OnHandQty)`), joined to `Erp.Part` in `TopLevel` for `Company = 'MFG01'`. |

### Acceptance Criteria
1. Create an `InnerSubQuery` named `WhseSum` on `Erp.PartWhse` grouping by `Company` and `PartNum`, with aggregated display fields `COUNT(WarehouseCode) AS WarehouseCount` and `SUM(OnHandQty) AS TotalOnHandQty` (`[B17]`).
2. In `TopLevel`, join `Erp.Part` to `WhseSum` (`inner` join on `Company`, `PartNum`) filtered to `Part.Company = 'MFG01'`.
3. Include display fields in order: `Part.Company`, `Part.PartNum`, `Part.PartDescription`, `Part.ClassID`, `WhseSum.WarehouseCount`, `WhseSum.TotalOnHandQty` (`[B18]`).
4. Sort results by `Part.PartNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B14.json /tmp/B14.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B14.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B14.json
```
