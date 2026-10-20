# Lab F06: Release Fulfillment Ratio Column Returns `0` for Every Partly Shipped Order (Fix Drill)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-306` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_F06_OrderReleaseFulfillment` |
| **Category** | BAQ Fix Drill |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Defective Starter File** | [`labs/baq/starter/F06.json`](starter/F06.json) |
| **Client-Reported Symptom** | Operations Management at `MFG01` runs `BAQ_F06_OrderReleaseFulfillment` for partly shipped orders `10061` through `10080` to track the proportion of fulfilled releases (`Calculated_FulfilledReleaseRatio` = `RelCounts_FulfilledReleases` divided by `RelCounts_TotalReleases`). Even though every order in the range shows `RelCounts_FulfilledReleases = 1` and `RelCounts_TotalReleases` of `2`, `3`, or `4` (which should yield `0.50`, `0.3333`, or `0.25`), `Calculated_FulfilledReleaseRatio` displays **`0`** on all 20 rows. |

### Required Deliverables
1. A written diagnosis explaining why `Calculated_FulfilledReleaseRatio` returns `0` despite its field data type being set to `decimal`.
2. The corrected BAQ JSON (`BAQ_F06_OrderReleaseFulfillment`) returning the decimal fulfillment ratio with a zero/null denominator guard.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Investigation & Verification Commands

```bash
# 1. Compile the starter BAQ to inspect the generated T-SQL Query Phrase
engines/baq/baq compile labs/baq/starter/F06.json

# 2. Save your corrected BAQ JSON and verify it compiles cleanly
engines/baq/baq compile /tmp/F06-fixed.json

# 3. On the SQL Server 2016 VM, run the corrected BAQ
engines/baq/baq run /tmp/F06-fixed.json
```
