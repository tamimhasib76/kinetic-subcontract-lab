# Lab F04: Closed Orders Still Appearing in Open Order Release Summary (Fix Drill)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-304` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_F04_OpenOrdersWithReleases` |
| **Category** | BAQ Fix Drill |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Defective Starter File** | [`labs/baq/starter/F04.json`](starter/F04.json) |
| **Client-Reported Symptom** | Materials Management at `MFG01` runs `BAQ_F04_OpenOrdersWithReleases` to inspect **open** orders in the range `10056` through `10065` along with each order's open release count (`OpenRelSub_OpenRelCount`). Even though orders `10056`–`10060` are closed (`OrderHed_OpenOrder = 0`), they still appear in the query results with blank `OpenRelSub_OpenRelCount` values, producing 10 rows instead of the 5 open orders (`10061`–`10065`). |

### Required Deliverables
1. A written diagnosis explaining why closed orders `10056`–`10060` are not excluded from the output.
2. The corrected BAQ JSON (`BAQ_F04_OpenOrdersWithReleases`) returning only the 5 open orders (`10061`–`10065`).

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Investigation & Verification Commands

```bash
# 1. Compile the starter BAQ to inspect the generated T-SQL Query Phrase
engines/baq/baq compile labs/baq/starter/F04.json

# 2. Save your corrected BAQ JSON and verify it compiles cleanly
engines/baq/baq compile /tmp/F04-fixed.json

# 3. On the SQL Server 2016 VM, run the corrected BAQ
engines/baq/baq run /tmp/F04-fixed.json
```
