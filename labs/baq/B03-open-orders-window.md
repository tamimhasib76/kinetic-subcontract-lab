# Lab B03: MFG01 Open Sales Orders in Order Range 10061–10070 (Single-Table)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-203` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B03_OpenOrdersWindow` |
| **Category** | Build Drill — Single-Table |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B03.json`](starter/B03.json) |
| **Summary** | Customer Service at MFG01 requests a BAQ (`BAQ_B03_OpenOrdersWindow`) on `Erp.OrderHed` returning open, non-void sales orders in `MFG01` with `OrderNum` between `10061` and `10070` inclusive. |

### Acceptance Criteria
1. Query table `Erp.OrderHed` filtered to `Company = 'MFG01'`, `OpenOrder = true`, `VoidOrder = false`, and `OrderNum BETWEEN 10061 AND 10070`.
2. Include display fields in order: `OrderHed.Company`, `OrderHed.OrderNum`, `OrderHed.CustNum`, `OrderHed.PONum`, `OrderHed.OrderDate`, `OrderHed.NeedByDate`, `OrderHed.OrderAmt`, `OrderHed.ProjManager_c` (`[B18]`).
3. Sort results by `OrderHed.OrderNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B03.json /tmp/B03.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B03.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B03.json
```
