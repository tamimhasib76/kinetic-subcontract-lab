# Lab B15: Customer Open Order Backlog Rollup (`InnerSubQuery`) (InnerSubQuery)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-215` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B15_CustomerOpenBacklog` |
| **Category** | Build Drill — InnerSubQuery |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B15.json`](starter/B15.json) |
| **Summary** | Finance at MFG01 requests a BAQ (`BAQ_B15_CustomerOpenBacklog`) summarizing open, non-void sales orders per customer in an `InnerSubQuery` (`OpenOrdSum`) and joining it to `Erp.Customer` in `TopLevel` for `Company = 'MFG01'` and `CustNum BETWEEN 1 AND 10`. |

### Acceptance Criteria
1. Create an `InnerSubQuery` named `OpenOrdSum` on `Erp.OrderHed` filtered to `OpenOrder = true` and `VoidOrder = false`, grouped by `Company` and `CustNum`, computing `COUNT(OrderNum) AS OpenOrderCount` and `SUM(OrderAmt) AS TotalOpenAmt` (`[B17]`).
2. In `TopLevel`, join `Erp.Customer` to `OpenOrdSum` (`inner` join on `Company`, `CustNum`) filtered to `Customer.Company = 'MFG01'` and `Customer.CustNum BETWEEN 1 AND 10`.
3. Include display fields in order: `Customer.Company`, `Customer.CustNum`, `Customer.CustID`, `Customer.Name`, `OpenOrdSum.OpenOrderCount`, `OpenOrdSum.TotalOpenAmt` (`[B18]`).
4. Sort results by `Customer.CustNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B15.json /tmp/B15.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B15.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B15.json
```
