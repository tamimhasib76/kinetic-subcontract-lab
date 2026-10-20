# Lab B06: Customer to ShipTo Addresses (`LEFT OUTER JOIN`) (Joins)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-206` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B06_CustomerShipToSites` |
| **Category** | Build Drill — Joins |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B06.json`](starter/B06.json) |
| **Summary** | Logistics at MFG01 needs a BAQ (`BAQ_B06_CustomerShipToSites`) listing `MFG01` customers `CustNum` `1` through `8` left-outer-joined to `Erp.ShipTo` so both primary (`MAIN`) and secondary (`PLANT2`) ship-to locations and special delivery instructions (`SpecialInstructions_c`) are returned. |

### Acceptance Criteria
1. Join `Erp.Customer` to `Erp.ShipTo` using a `left` (`LEFT OUTER JOIN`) relation on `Company = Company` and `CustNum = CustNum` (`[B2]`).
2. Filter `Customer` to `Company = 'MFG01'` and `CustNum BETWEEN 1 AND 8`.
3. Include display fields in order: `Customer.Company`, `Customer.CustNum`, `Customer.CustID`, `Customer.Name`, `ShipTo.ShipToNum`, `ShipTo.Name`, `ShipTo.City`, `ShipTo.SpecialInstructions_c` (`[B18]`).
4. Sort results by `Customer.CustNum ASC`, `ShipTo.ShipToNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B06.json /tmp/B06.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B06.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B06.json
```
