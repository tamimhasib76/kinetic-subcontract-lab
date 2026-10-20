# Lab B07: Order Lines Joined to Part Master Specifications (Joins)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-207` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B07_OrderLinePartSpecs` |
| **Category** | Build Drill — Joins |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B07.json`](starter/B07.json) |
| **Summary** | Production Control at MFG01 needs a 3-table BAQ (`BAQ_B07_OrderLinePartSpecs`) joining `Erp.OrderHed`, `Erp.OrderDtl`, and `Erp.Part` for orders `10061` through `10065` in `MFG01` to view line revision, extended weight, and part steel gauge (`SteelGauge_c`). |

### Acceptance Criteria
1. Join `Erp.OrderHed` -> `Erp.OrderDtl` (`inner` join on `Company`, `OrderNum`) and `Erp.OrderDtl` -> `Erp.Part` (`inner` join on `Company`, `PartNum`).
2. Filter `OrderHed` to `Company = 'MFG01'` and `OrderNum BETWEEN 10061 AND 10065`.
3. Include display fields in order: `OrderHed.Company`, `OrderHed.OrderNum`, `OrderDtl.OrderLine`, `OrderDtl.PartNum`, `Part.PartDescription`, `Part.ClassID`, `Part.SteelGauge_c`, `OrderDtl.RevisionNum`, `OrderDtl.OrderQty`, `OrderDtl.ExtWeight` (`[B18]`).
4. Sort results by `OrderHed.OrderNum ASC`, `OrderDtl.OrderLine ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B07.json /tmp/B07.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B07.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B07.json
```
