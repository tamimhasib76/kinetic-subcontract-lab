# Lab F01: Duplicate Order Rows Showing Unknown Customer Names (Fix Drill)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-301` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_F01_CustomerOrders` |
| **Category** | BAQ Fix Drill |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Defective Starter File** | [`labs/baq/starter/F01.json`](starter/F01.json) |
| **Client-Reported Symptom** | When Sales Operations at `MFG01` runs `BAQ_F01_CustomerOrders` for open orders `10101` through `10110`, the query returns **20 rows instead of 10**. Every order number appears twice: once with the expected `MFG01` customer name (such as *Vortex Heavy Engineering*, *Apex Dynamics Ltd*, or *Buckeye State Stamping*) and a second time with an unfamiliar Michigan customer name (such as *Lansing Assembly Systems*, *Huron Industrial Hydraulics*, or *Acme Global Midwest Division*). |

### Required Deliverables
1. A written diagnosis identifying the root cause in the BAQ definition that makes each order appear twice with an unfamiliar customer name.
2. The corrected BAQ JSON (`BAQ_F01_CustomerOrders`) returning the exact 10 `MFG01` rows (`10101`–`10110`) with their true customer `CustID` and `Name`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Investigation & Verification Commands

```bash
# 1. Compile the starter BAQ to inspect the generated T-SQL Query Phrase
engines/baq/baq compile labs/baq/starter/F01.json

# 2. Save your corrected BAQ JSON and verify it compiles cleanly
engines/baq/baq compile /tmp/F01-fixed.json

# 3. On the SQL Server 2016 VM, run the corrected BAQ
engines/baq/baq run /tmp/F01-fixed.json
```
