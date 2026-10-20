# Lab F05: Overdue Days Count Displays 55–69 Days Instead of 1–15 Days (Fix Drill)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-305` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_F05_LateBacklogAging` |
| **Category** | BAQ Fix Drill |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Defective Starter File** | [`labs/baq/starter/F05.json`](starter/F05.json) |
| **Client-Reported Symptom** | Customer Service at `MFG01` runs `BAQ_F05_LateBacklogAging` for open orders `10061` through `10075`. Per the report specification, `Calculated_DaysPastNeedBy` must report the number of days between the order header **Need By Date** (`OrderHed.NeedByDate`) and the lab reference date (`Constants.Today`, `2026-10-15`). Although orders `10061`–`10075` have `OrderHed_NeedByDate` values between `2026-09-30` and `2026-10-14` (1 to 15 days before `2026-10-15`), `Calculated_DaysPastNeedBy` outputs `69` down to `55` days. |

### Required Deliverables
1. A written diagnosis explaining why `Calculated_DaysPastNeedBy` outputs `55`–`69` days instead of `1`–`15` days.
2. The corrected BAQ JSON (`BAQ_F05_LateBacklogAging`) computing `Calculated_DaysPastNeedBy` from `OrderHed.NeedByDate`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Investigation & Verification Commands

```bash
# 1. Compile the starter BAQ to inspect the generated T-SQL Query Phrase
engines/baq/baq compile labs/baq/starter/F05.json

# 2. Save your corrected BAQ JSON and verify it compiles cleanly
engines/baq/baq compile /tmp/F05-fixed.json

# 3. On the SQL Server 2016 VM, run the corrected BAQ
engines/baq/baq run /tmp/F05-fixed.json
```
