# Phase 2b BAQ Lab Drills (`labs/baq/`)

This directory contains **15 BAQ build drills (`B01`–`B15`)** and **6 BAQ troubleshooting/fix drills (`F01`–`F06`)** targeting `[ErpLab].[Erp].*` (Microsoft SQL Server 2016).

> **Default chosen for the lab, not confirmed against Epicor.**
> See [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).

---

## 1. Build Drills (`B01`–`B15`)

- **4 Single-Table Drills (`B01`–`B04`)**
- **5 Join Drills (`B05`–`B09`)**
- **4 Calculated-Field Drills (`B10`–`B13`)**
- **2 Simple `InnerSubQuery` Drills (`B14`–`B15`)**

| Drill | Ticket ID | Category | Ticket Spec | Starter BAQ JSON |
| :--- | :--- | :--- | :--- | :--- |
| `B01` | `KIN-BAQ-201` | Single-Table | [`B01-customer-directory.md`](B01-customer-directory.md) | [`starter/B01.json`](starter/B01.json) |
| `B02` | `KIN-BAQ-202` | Single-Table | [`B02-ppap-parts-catalog.md`](B02-ppap-parts-catalog.md) | [`starter/B02.json`](starter/B02.json) |
| `B03` | `KIN-BAQ-203` | Single-Table | [`B03-open-orders-window.md`](B03-open-orders-window.md) | [`starter/B03.json`](starter/B03.json) |
| `B04` | `KIN-BAQ-204` | Single-Table | [`B04-shipments-tracking-list.md`](B04-shipments-tracking-list.md) | [`starter/B04.json`](starter/B04.json) |
| `B05` | `KIN-BAQ-205` | Joins | [`B05-orders-with-customer.md`](B05-orders-with-customer.md) | [`starter/B05.json`](starter/B05.json) |
| `B06` | `KIN-BAQ-206` | Joins | [`B06-customer-shipto-left-join.md`](B06-customer-shipto-left-join.md) | [`starter/B06.json`](starter/B06.json) |
| `B07` | `KIN-BAQ-207` | Joins | [`B07-order-lines-part-specs.md`](B07-order-lines-part-specs.md) | [`starter/B07.json`](starter/B07.json) |
| `B08` | `KIN-BAQ-208` | Joins | [`B08-packslip-customer-lines.md`](B08-packslip-customer-lines.md) | [`starter/B08.json`](starter/B08.json) |
| `B09` | `KIN-BAQ-209` | Joins | [`B09-invoice-register-shipto.md`](B09-invoice-register-shipto.md) | [`starter/B09.json`](starter/B09.json) |
| `B10` | `KIN-BAQ-210` | Calculated Fields | [`B10-line-extended-amount.md`](B10-line-extended-amount.md) | [`starter/B10.json`](starter/B10.json) |
| `B11` | `KIN-BAQ-211` | Calculated Fields | [`B11-late-orders-days-late.md`](B11-late-orders-days-late.md) | [`starter/B11.json`](starter/B11.json) |
| `B12` | `KIN-BAQ-212` | Calculated Fields | [`B12-order-value-tier-case.md`](B12-order-value-tier-case.md) | [`starter/B12.json`](starter/B12.json) |
| `B13` | `KIN-BAQ-213` | Calculated Fields | [`B13-shipped-ratio-decimal-cast.md`](B13-shipped-ratio-decimal-cast.md) | [`starter/B13.json`](starter/B13.json) |
| `B14` | `KIN-BAQ-214` | InnerSubQuery | [`B14-part-onhand-subquery.md`](B14-part-onhand-subquery.md) | [`starter/B14.json`](starter/B14.json) |
| `B15` | `KIN-BAQ-215` | InnerSubQuery | [`B15-customer-open-backlog-subquery.md`](B15-customer-open-backlog-subquery.md) | [`starter/B15.json`](starter/B15.json) |

---

## 2. Fix Drills (`F01`–`F06`)

Each fix drill provides a client-reported symptom and a BAQ JSON file in [`starter/`](starter/) containing a planted defect. For each ticket, write a root-cause diagnosis and produce the corrected BAQ JSON.

| Drill | Ticket ID | Ticket Spec (Client Symptom) | Defective BAQ JSON |
| :--- | :--- | :--- | :--- |
| `F01` | `KIN-BAQ-301` | [`F01-duplicate-customer-orders.md`](F01-duplicate-customer-orders.md) | [`starter/F01.json`](starter/F01.json) |
| `F02` | `KIN-BAQ-302` | [`F02-wrong-orders-for-accounts.md`](F02-wrong-orders-for-accounts.md) | [`starter/F02.json`](starter/F02.json) |
| `F03` | `KIN-BAQ-303` | [`F03-inflated-line-backlog.md`](F03-inflated-line-backlog.md) | [`starter/F03.json`](starter/F03.json) |
| `F04` | `KIN-BAQ-304` | [`F04-closed-orders-in-backlog.md`](F04-closed-orders-in-backlog.md) | [`starter/F04.json`](starter/F04.json) |
| `F05` | `KIN-BAQ-305` | [`F05-overdue-days-mismatch.md`](F05-overdue-days-mismatch.md) | [`starter/F05.json`](starter/F05.json) |
| `F06` | `KIN-BAQ-306` | [`F06-zero-fulfillment-rate.md`](F06-zero-fulfillment-rate.md) | [`starter/F06.json`](starter/F06.json) |
