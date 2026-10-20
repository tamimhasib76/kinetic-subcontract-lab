# Lab B02: PPAP-Required Parts Catalog (Single-Table)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-202` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B02_PPAPParts` |
| **Category** | Build Drill — Single-Table |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B02.json`](starter/B02.json) |
| **Summary** | Quality Engineering at MFG01 requires a BAQ (`BAQ_B02_PPAPParts`) on `Erp.Part` listing all parts in company `MFG01` where the user-defined PPAP flag (`PPAP_c`) is true (`1`). |

### Acceptance Criteria
1. Query table `Erp.Part` filtered to `Company = 'MFG01'` and `PPAP_c = true` (`1`).
2. Include display fields in order: `Part.Company`, `Part.PartNum`, `Part.PartDescription`, `Part.ClassID`, `Part.IUM`, `Part.UnitPrice`, `Part.SteelGauge_c`, `Part.PPAP_c` (`[B18]`).
3. Sort results by `Part.PartNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B02.json /tmp/B02.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B02.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B02.json
```
