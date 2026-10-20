# Lab F02: Silent Wrong Order Matches for Regional Accounts `'10'`, `'12'`, and `'15'` (Fix Drill)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-302` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_F02_RegionalAccountOrders` |
| **Category** | BAQ Fix Drill |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Defective Starter File** | [`labs/baq/starter/F02.json`](starter/F02.json) |
| **Client-Reported Symptom** | Regional Account Managers at `MFG01` run `BAQ_F02_RegionalAccountOrders` to list open orders for commercial accounts `'10'` (*Precision Dynamics 10*), `'12'` (*Precision Dynamics 12*), and `'15'` (*Precision Dynamics 15*). The query executes without error, but returns the wrong orders (`10079`, `10081`, `10084`, `10102`, `10104`, `10107`, `10125`, `10127`, `10130`, `10148`, `10150` — which belong to *Canton Foundry & Forge*, *Toledo Gear Systems*, and *Lorain Marine Hardware*) while missing the actual open orders placed by *Precision Dynamics 10*, *12*, and *15* (`10067`–`10069`, `10090`–`10092`, `10113`–`10115`, `10136`–`10138`). |

### Required Deliverables
1. A written diagnosis identifying the root cause in the BAQ definition that causes the query to return another customer's orders instead of the orders placed by *Precision Dynamics 10*, *12*, and *15*.
2. The corrected BAQ JSON (`BAQ_F02_RegionalAccountOrders`) returning the 12 open orders belonging to accounts `'10'`, `'12'`, and `'15'`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Investigation & Verification Commands

```bash
# 1. Compile the starter BAQ to inspect the generated T-SQL Query Phrase
engines/baq/baq compile labs/baq/starter/F02.json

# 2. Save your corrected BAQ JSON and verify it compiles cleanly
engines/baq/baq compile /tmp/F02-fixed.json

# 3. On the SQL Server 2016 VM, run the corrected BAQ
engines/baq/baq run /tmp/F02-fixed.json
```
