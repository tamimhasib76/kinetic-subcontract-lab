# Lab B05: Open Sales Orders Joined to Sold-To Customer (Joins)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-205` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B05_OrdersWithCustomer` |
| **Category** | Build Drill — Joins |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B05.json`](starter/B05.json) |
| **Summary** | Sales Operations at MFG01 needs a BAQ (`BAQ_B05_OrdersWithCustomer`) joining `Erp.OrderHed` to `Erp.Customer` for open orders `10101` through `10115` in `MFG01` so the customer's `CustID` and `Name` appear alongside order header details. |

### Acceptance Criteria
1. Join `Erp.OrderHed` to `Erp.Customer` (`inner` join on `Company = Company` and `CustNum = CustNum` `[B2]`).
2. Filter `OrderHed` to `Company = 'MFG01'`, `OpenOrder = true`, and `OrderNum BETWEEN 10101 AND 10115`.
3. Include display fields in order: `OrderHed.Company`, `OrderHed.OrderNum`, `Customer.CustID`, `Customer.Name`, `OrderHed.PONum`, `OrderHed.OrderDate`, `OrderHed.NeedByDate`, `OrderHed.OrderAmt` (`[B18]`).
4. Sort results by `OrderHed.OrderNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B05.json /tmp/B05.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B05.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B05.json
```
