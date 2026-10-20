# Lab F03: Repeated Order Lines and Tripled Quantities in Schedule Export (Fix Drill)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-303` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_F03_StaggeredLineSchedule` |
| **Category** | BAQ Fix Drill |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Defective Starter File** | [`labs/baq/starter/F03.json`](starter/F03.json) |
| **Client-Reported Symptom** | Production Planning at `MFG01` runs `BAQ_F03_StaggeredLineSchedule` to see one row per open order line for orders `10061` through `10070` along with the line's total release count (`RelSummary_ReleaseCount`) and earliest release request date (`RelSummary_EarliestReqDate`). Instead of returning 10 rows (one for each open Line 2 on orders `10061`–`10070`), the BAQ returns **30 rows** — repeating every order line three times and tripling `OrderDtl_OrderQty` (`450.0000` total instead of `150.0000`) when planners sum the export. |

### Required Deliverables
1. A written diagnosis explaining why each order line is repeated three times in the output.
2. The corrected BAQ JSON (`BAQ_F03_StaggeredLineSchedule`) returning exactly 1 row per open order line (10 rows total) with `RelSummary_ReleaseCount` (`3`) and `RelSummary_EarliestReqDate` (`MIN(ReqDate)`).

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Investigation & Verification Commands

```bash
# 1. Compile the starter BAQ to inspect the generated T-SQL Query Phrase
engines/baq/baq compile labs/baq/starter/F03.json

# 2. Save your corrected BAQ JSON and verify it compiles cleanly
engines/baq/baq compile /tmp/F03-fixed.json

# 3. On the SQL Server 2016 VM, run the corrected BAQ
engines/baq/baq run /tmp/F03-fixed.json
```
