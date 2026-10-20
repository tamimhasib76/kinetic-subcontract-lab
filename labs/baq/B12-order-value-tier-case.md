# Lab B12: Order Priority Classification (`CASE WHEN` & `ISNULL`) (Calculated Fields)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-212` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B12_OrderValueTier` |
| **Category** | Build Drill — Calculated Fields |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B12.json`](starter/B12.json) |
| **Summary** | Operations at MFG01 requests a BAQ (`BAQ_B12_OrderValueTier`) on `Erp.OrderHed` for open orders `10065` through `10080` in `MFG01` with a calculated field `ValueTier` (`Calculated_ValueTier`) classifying `OrderAmt` as `'HIGH'` (`>= 1500.00`), `'MEDIUM'` (`>= 875.00`), or `'STANDARD'`. |

### Acceptance Criteria
1. Query `Erp.OrderHed` filtered to `Company = 'MFG01'`, `OpenOrder = true`, and `OrderNum BETWEEN 10065 AND 10080`.
2. Include display fields: `OrderHed.Company`, `OrderHed.OrderNum`, `OrderHed.CustNum`, `OrderHed.OrderAmt` (`[B18]`).
3. Add calculated field `ValueTier` (`dataType: 'nvarchar'`) using `CASE WHEN ISNULL([OrderHed].[OrderAmt], 0) >= 1500.00 THEN N'HIGH' WHEN ISNULL([OrderHed].[OrderAmt], 0) >= 875.00 THEN N'MEDIUM' ELSE N'STANDARD' END` (`[B8, B12]`).
4. Sort results by `OrderHed.OrderNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B12.json /tmp/B12.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B12.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B12.json
```
