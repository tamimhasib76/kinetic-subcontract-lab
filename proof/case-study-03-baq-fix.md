# Case Study 03: BAQ Defect Diagnosis & SQL Compilation (One-Page Summary)

> **Notice**: Lab exercise on synthetic data. Not client work.
>
> **Synthetic Lab Disclosure & Environment Notice**: All queries below target the synthetic `[ErpLab].[Erp].*` schema (`MFG01`) from [`labs/baq/`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/labs/baq). No SQL Server instance ran on this authoring host; row counts and runtime query results are marked `[to be captured on the VM]`. The offline BAQ compiler (`python3 engines/baq/cli.py compile`) was executed locally in this session to produce the verified SQL outputs below.
> **Lab Banner**: *"Default chosen for the lab, not confirmed against Epicor."*

---

## 1. Two Classic BAQ Defects Diagnosed (`docs/reference/02-baq.md`)

1. **Drill F01 — Missing `Company = Company` Join (`02-baq.md` §1.1 `[B4, B5]`, Defect #1)**:
   - **Symptom**: `OrderHed` filtered to `Company = 'MFG01'` and an `OrderNum` range returns duplicate rows [row counts to be captured on the VM], pairing each `MFG01` order with both `MFG01` and `MFG02` customer records sharing the same integer `CustNum`.
   - **Fix**: Add `OrderHed.Company = Customer.Company` to the table relation (`[B4, B5]`).
2. **Drill F06 — Integer Division Truncation (`02-baq.md` §2.1 `[M1]`, Defect #6)**:
   - **Symptom**: Calculated field `[RelCounts].[FulfilledReleases] / [RelCounts].[TotalReleases]` divides two `INT` columns, truncating fractional fulfillment ratios to `0` [query results to be captured on the VM].
   - **Fix**: Cast operands to `DECIMAL(7,2)` before dividing and guard against a zero denominator (`[M1]`).

---

## 2. Compiler Output: Drill F01 (`python3 engines/baq/cli.py compile`)

### Before Fix (`labs/baq/starter/F01.json` — Missing `Company = Company`)
```sql
-- BAQ ID: BAQ_F01_CustomerOrders
-- Description: MFG01 open orders 10101-10110 with customer account details
-- Target: Microsoft SQL Server 2016+ ([ErpLab].[Erp].*)
-- Banner: Default chosen for the lab, not confirmed against Epicor.
SELECT
    [OrderHed].[Company] AS [OrderHed_Company],
    [OrderHed].[OrderNum] AS [OrderHed_OrderNum],
    [OrderHed].[CustNum] AS [OrderHed_CustNum],
    [Customer].[CustID] AS [Customer_CustID],
    [Customer].[Name] AS [Customer_Name],
    [OrderHed].[PONum] AS [OrderHed_PONum],
    [OrderHed].[OrderAmt] AS [OrderHed_OrderAmt]
FROM [ErpLab].[Erp].[OrderHed] AS [OrderHed]
INNER JOIN [ErpLab].[Erp].[Customer] AS [Customer]
    ON [OrderHed].[CustNum] = [Customer].[CustNum]
WHERE [OrderHed].[Company] = N'MFG01'
  AND [OrderHed].[OpenOrder] = 1
  AND [OrderHed].[OrderNum] BETWEEN 10101 AND 10110
ORDER BY [OrderHed].[OrderNum] ASC, [Customer].[CustID] ASC;
```

### After Fix (`Company = Company` Added to Join Relation)
```sql
INNER JOIN [ErpLab].[Erp].[Customer] AS [Customer]
    ON [OrderHed].[Company] = [Customer].[Company]
   AND [OrderHed].[CustNum] = [Customer].[CustNum]
```

---

## 3. Compiler Output: Drill F06 (`python3 engines/baq/cli.py compile`)

### Before Fix (`labs/baq/starter/F06.json` — `INT / INT` Truncation)
```sql
SELECT
    [OrderHed].[Company] AS [OrderHed_Company],
    [OrderHed].[OrderNum] AS [OrderHed_OrderNum],
    [RelCounts].[FulfilledReleases] AS [RelCounts_FulfilledReleases],
    [RelCounts].[TotalReleases] AS [RelCounts_TotalReleases],
    [RelCounts].[FulfilledReleases] / [RelCounts].[TotalReleases] AS [Calculated_FulfilledReleaseRatio]
FROM [ErpLab].[Erp].[OrderHed] AS [OrderHed]
```

### After Fix (`DECIMAL` Cast & Zero-Denominator Guard `[M1]`)
```sql
SELECT
    [OrderHed].[Company] AS [OrderHed_Company],
    [OrderHed].[OrderNum] AS [OrderHed_OrderNum],
    [RelCounts].[FulfilledReleases] AS [RelCounts_FulfilledReleases],
    [RelCounts].[TotalReleases] AS [RelCounts_TotalReleases],
    CASE WHEN ISNULL([RelCounts].[TotalReleases], 0) <> 0 THEN CAST([RelCounts].[FulfilledReleases] AS DECIMAL(7,2)) / CAST([RelCounts].[TotalReleases] AS DECIMAL(7,2)) ELSE 0 END AS [Calculated_FulfilledReleaseRatio]
FROM [ErpLab].[Erp].[OrderHed] AS [OrderHed]
```
