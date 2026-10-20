# Lab B11: Late Open Order Aging (`DATEDIFF` with `Constants.Today`) (Calculated Fields)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-211` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B11_LateOrderAging` |
| **Category** | Build Drill — Calculated Fields |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B11.json`](starter/B11.json) |
| **Summary** | Customer Service at MFG01 needs a BAQ (`BAQ_B11_LateOrderAging`) on `Erp.OrderHed` joined to `Erp.Customer` for late open orders `10061` through `10075` in `MFG01`, adding an integer calculated field `DaysLate` (`Calculated_DaysLate`) that computes `DATEDIFF(day, [OrderHed].[NeedByDate], Constants.Today)`. |

### Acceptance Criteria
1. Join `Erp.OrderHed` to `Erp.Customer` (`inner` join on `Company`, `CustNum`) filtered to `OrderHed.Company = 'MFG01'`, `OrderHed.OpenOrder = true`, and `OrderHed.OrderNum BETWEEN 10061 AND 10075`.
2. Include display fields: `OrderHed.Company`, `OrderHed.OrderNum`, `Customer.CustID`, `OrderHed.NeedByDate` (`[B18]`).
3. Add calculated field `DaysLate` (`dataType: 'int'`) with expression `DATEDIFF(day, [OrderHed].[NeedByDate], Constants.Today)` (`[B11]`, `sql/00-README.md` §2).
4. Sort results by `OrderHed.OrderNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B11.json /tmp/B11.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B11.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B11.json
```
