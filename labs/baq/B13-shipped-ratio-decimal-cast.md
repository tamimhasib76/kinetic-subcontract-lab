# Lab B13: Shipment Line Fill Ratio with Zero-Denominator Guard (Calculated Fields)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-213` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B13_ShipmentFillRatio` |
| **Category** | Build Drill — Calculated Fields |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B13.json`](starter/B13.json) |
| **Summary** | Warehouse Management at MFG01 needs a BAQ (`BAQ_B13_ShipmentFillRatio`) joining `Erp.ShipDtl` to `Erp.OrderDtl` for packs `50074` through `50082` in `MFG01` with a calculated field `ShippedFillRatio` (`Calculated_ShippedFillRatio`) dividing `ShipDtl.SellingShippedQty` by `OrderDtl.SellingQuantity` using `CAST(... AS DECIMAL(7,2))` and guarding against a zero/null denominator. |

### Acceptance Criteria
1. Join `Erp.ShipDtl` to `Erp.OrderDtl` (`inner` join on `Company`, `OrderNum`, `OrderLine`) filtered to `ShipDtl.Company = 'MFG01'` and `ShipDtl.PackNum BETWEEN 50074 AND 50082`.
2. Include display fields: `ShipDtl.Company`, `ShipDtl.PackNum`, `ShipDtl.OrderNum`, `ShipDtl.OrderLine`, `ShipDtl.PartNum`, `ShipDtl.SellingShippedQty`, `OrderDtl.SellingQuantity` (`[B18]`).
3. Add calculated field `ShippedFillRatio` (`dataType: 'decimal'`) with expression `CASE WHEN ISNULL([OrderDtl].[SellingQuantity], 0) <> 0 THEN CAST([ShipDtl].[SellingShippedQty] AS DECIMAL(7,2)) / CAST([OrderDtl].[SellingQuantity] AS DECIMAL(7,2)) ELSE 0 END` (`[B8, B9, M1]`).
4. Sort results by `ShipDtl.PackNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B13.json /tmp/B13.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B13.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B13.json
```
