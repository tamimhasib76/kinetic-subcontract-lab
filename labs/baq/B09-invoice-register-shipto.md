# Lab B09: AR Invoice Line Register with Customer and Ship-To Name (Joins)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-209` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B09_InvoiceRegister` |
| **Category** | Build Drill — Joins |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B09.json`](starter/B09.json) |
| **Summary** | Finance at MFG01 requests a 4-table BAQ (`BAQ_B09_InvoiceRegister`) joining `Erp.InvcHead`, `Erp.InvcDtl`, `Erp.Customer`, and `Erp.ShipTo` for invoices `90001` through `90005` in `MFG01`. |

### Acceptance Criteria
1. Join `Erp.InvcHead` -> `Erp.InvcDtl` (`inner` join on `Company`, `InvoiceNum`), `Erp.InvcHead` -> `Erp.Customer` (`inner` join on `Company`, `CustNum`), and `Erp.InvcDtl` -> `Erp.ShipTo` (`left` join on `Company = Company`, `ShipToCustNum = CustNum`, `ShipToNum = ShipToNum` `[S17, B2]`).
2. Filter `InvcHead` to `Company = 'MFG01'` and `InvoiceNum BETWEEN 90001 AND 90005`.
3. Include display fields in order: `InvcHead.Company`, `InvcHead.InvoiceNum`, `InvcHead.InvoiceDate`, `Customer.CustID`, `InvcHead.ShipToPONum_c`, `InvcDtl.InvoiceLine`, `InvcDtl.PartNum`, `InvcDtl.SellingShipQty`, `InvcDtl.ExtPrice`, `ShipTo.Name` (`[B18]`).
4. Sort results by `InvcHead.InvoiceNum ASC`, `InvcDtl.InvoiceLine ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B09.json /tmp/B09.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B09.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B09.json
```
