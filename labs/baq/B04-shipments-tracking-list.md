# Lab B04: MFG01 Shipment Manifest Range (Packs 50001–50010) (Single-Table)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-204` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B04_ShipmentManifest` |
| **Category** | Build Drill — Single-Table |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B04.json`](starter/B04.json) |
| **Summary** | Shipping at MFG01 requests a BAQ (`BAQ_B04_ShipmentManifest`) on `Erp.ShipHead` listing shipped packs `50001` through `50010` in `MFG01` with carrier, tracking number, and weight. |

### Acceptance Criteria
1. Query table `Erp.ShipHead` filtered to `Company = 'MFG01'`, `ShipStatus = 'SHIPPED'`, and `PackNum BETWEEN 50001 AND 50010`.
2. Include display fields in order: `ShipHead.Company`, `ShipHead.PackNum`, `ShipHead.CustNum`, `ShipHead.ShipDate`, `ShipHead.ShipViaCode`, `ShipHead.TrackingNumber`, `ShipHead.Weight`, `ShipHead.ShipStatus` (`[B18]`).
3. Sort results by `ShipHead.PackNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B04.json /tmp/B04.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B04.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B04.json
```
