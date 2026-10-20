# Lab B08: Packing Slip Lines with Customer and Customer Part Number (Joins)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-208` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B08_PackSlipLines` |
| **Category** | Build Drill — Joins |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B08.json`](starter/B08.json) |
| **Summary** | Shipping at MFG01 needs a BAQ (`BAQ_B08_PackSlipLines`) joining `Erp.ShipHead`, `Erp.ShipDtl`, and `Erp.Customer` for packs `50001` through `50005` in `MFG01` to audit customer part numbers (`CustPartNum`) and shipped quantities. |

### Acceptance Criteria
1. Join `Erp.ShipHead` -> `Erp.ShipDtl` (`inner` join on `Company`, `PackNum`) and `Erp.ShipHead` -> `Erp.Customer` (`inner` join on `Company`, `CustNum`).
2. Filter `ShipHead` to `Company = 'MFG01'` and `PackNum BETWEEN 50001 AND 50005`.
3. Include display fields in order: `ShipHead.Company`, `ShipHead.PackNum`, `ShipHead.ShipDate`, `Customer.CustID`, `Customer.Name`, `ShipDtl.PackLine`, `ShipDtl.OrderNum`, `ShipDtl.PartNum`, `ShipDtl.CustPartNum`, `ShipDtl.SellingShippedQty` (`[B18]`).
4. Sort results by `ShipHead.PackNum ASC`, `ShipDtl.PackLine ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B08.json /tmp/B08.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B08.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B08.json
```
