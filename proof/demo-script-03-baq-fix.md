# 5-Minute Demo Script 03: BAQ Defect Diagnosis & Offline T-SQL Compilation

> **Notice**: Lab exercise on synthetic data. Not client work.
>
> **Synthetic Lab Disclosure & Environment Notice**: Uses synthetic BAQ JSON definitions targeting `[ErpLab].[Erp].*` (`labs/baq/starter/F01.json` and `labs/baq/starter/F06.json`). No SQL Server instance ran here; row counts and runtime query results are marked `[to be captured on the VM]`. All compilation steps run the offline compiler `python3 engines/baq/cli.py compile`.
> **Lab Banner**: *"Default chosen for the lab, not confirmed against Epicor."*

---

## Timing & Pacing Overview (Total: 5:00)

| Segment | Time | Screen / Artifact Shown | Objective |
|---| :---: |---|---|
| **1. Symptom Review** | `0:00 – 1:00` | [`labs/baq/F01-duplicate-customer-orders.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/labs/baq/F01-duplicate-customer-orders.md) & [`labs/baq/F06-zero-fulfillment-rate.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/labs/baq/F06-zero-fulfillment-rate.md) | Frame the two production-style BAQ symptoms: doubled multi-company rows and zero fulfillment ratios [runtime results to be captured on the VM]. |
| **2. Compiling Defective `F01`** | `1:00 – 2:30` | Terminal (`baq compile labs/baq/starter/F01.json`) | Show the generated `INNER JOIN` missing `Company = Company` (`[B4, B5]`) and repair it. |
| **3. Compiling Defective `F06`** | `2:30 – 4:15` | Terminal (`baq compile labs/baq/starter/F06.json`) | Show `INT / INT` truncation in `[RelCounts].[FulfilledReleases] / [RelCounts].[TotalReleases]` (`[M1]`) and apply the `DECIMAL` cast. |
| **4. Wrap-Up & Guardrails** | `4:15 – 5:00` | [`case-study-03-baq-fix.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/case-study-03-baq-fix.md) | Summarize the 6 Phase 2b BAQ fix-drill defects (`02-baq.md`). |

---

## Minute-by-Minute Script

### `0:00 – 1:00` · 1. Framing the Two BAQ Fix Drills
- **Action**: Display [`proof/case-study-03-baq-fix.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/case-study-03-baq-fix.md) Section 1.
- **Talk Track**:
  - *"In our synthetic two-company database (`MFG01` and `MFG02`), integer `CustNum` values exist in both companies (`[D10]`). We will diagnose and compile two broken BAQ definitions offline using `engines/baq/cli.py compile`."*

### `1:00 – 2:30` · 2. Live Compile of Drill F01 (Missing `Company = Company` Join)
- **Action**: Run in terminal:
  ```bash
  python3 engines/baq/cli.py compile labs/baq/starter/F01.json
  ```
- **Output Highlighted**:
  ```sql
  INNER JOIN [ErpLab].[Erp].[Customer] AS [Customer]
      ON [OrderHed].[CustNum] = [Customer].[CustNum]
  ```
- **Talk Track**:
  - *"Look at the `INNER JOIN`: `OrderHed` is filtered to `MFG01`, but the join to `Customer` only matches `CustNum = CustNum`. Per `02-baq.md` §1.1 (`[B4, B5]`), joining multi-company tables without `Company = Company` pulls matching `CustNum` rows from `MFG02` as well, duplicating order rows [exact row counts to be captured on the VM]."*
  - *"Adding `Company = Company` to the relation emits `ON [OrderHed].[Company] = [Customer].[Company] AND [OrderHed].[CustNum] = [Customer].[CustNum]`, restoring single-company integrity [row counts to be captured on the VM]."*

### `2:30 – 4:15` · 3. Live Compile of Drill F06 (Integer Division Truncation)
- **Action**: Run in terminal:
  ```bash
  python3 engines/baq/cli.py compile labs/baq/starter/F06.json
  ```
- **Output Highlighted**:
  ```sql
  [RelCounts].[FulfilledReleases] / [RelCounts].[TotalReleases] AS [Calculated_FulfilledReleaseRatio]
  ```
- **Talk Track**:
  - *"In `F06`, the `RelCounts` subquery counts `TotalReleases` (`COUNT`) and `FulfilledReleases` (`SUM(CASE ... THEN 1 ELSE 0 END)`). Both are T-SQL integers. Per `02-baq.md` §2.1 (`[M1]`), dividing two integers truncates any fraction below `1` to `0`."*
  - *"Wrapping the operands in `CAST(... AS DECIMAL(7,2))` inside a `CASE WHEN ISNULL([RelCounts].[TotalReleases], 0) <> 0` guard compiles cleanly and preserves the exact decimal ratio [query results to be captured on the VM]."*

### `4:15 – 5:00` · 4. Summary of the 6 BAQ Fix-Drill Defects
- **Action**: Point to `docs/reference/02-baq.md` ("Phase 2b fix-drill defects").
- **Talk Track**:
  - *"Every BAQ review checks the same six failure modes: (1) missing `Company = Company` join, (2) `CustNum = CustID` int-vs-varchar join causing SQL error 245, (3) unaggregated `OrderRel` join multiplying line totals, (4) filter criteria placed on the wrong subquery, (5) filtering `OrderDate` instead of `NeedByDate`, and (6) integer division truncation."*
