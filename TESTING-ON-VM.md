# TESTING-ON-VM.md: SSRS 2016 VM Testing & Verification Checklist

> **CRITICAL ENVIRONMENT NOTICE:**
> There is **no SQL Server or SSRS on this development machine**. No scripts, procedures, or reports were executed, deployed, or rendered locally.
> This document specifies the exact, reproducible execution checklist and validation protocol to be run on the target **Windows Server 2016 + SQL Server 2016 + SSRS 2016** test virtual machine.

---

## 1. Target Environment Specifications

- **Operating System**: Microsoft Windows Server 2016 Standard or Datacenter (x64)
- **Database Engine**: Microsoft SQL Server 2016 SP2+ (Standard, Developer, or Enterprise Edition)
- **Reporting Services**: SQL Server Reporting Services (SSRS) 2016 in Native Mode
- **Report Designer**: Microsoft Report Builder 2016 (Build 15.0.900) / Visual Studio SSDT 2015/2017
- **Tools**: SQL Server Management Studio (SSMS) 18.x+, Windows PowerShell 5.1

---

## 2. Step 1: Database Initialization (`sql/01`, `sql/02`, and `sql/03`)

### 1.1 Execute Core Application Schema (`sql/01-erp-app-schema.sql`)
1. Open SSMS on the Windows Server 2016 VM and connect to the local SQL Server instance (`localhost`).
2. Open and execute `sql/01-erp-app-schema.sql` (or run via command prompt):
   ```cmd
   sqlcmd -S localhost -E -i "C:\kinetic-subcontract-lab\sql\01-erp-app-schema.sql"
   ```
3. **Verification Checklist:**
   - [ ] Database `[ErpLab]` is created.
   - [ ] Schema `[Erp]` is created.
   - [ ] Core tables created: `Company`, `LabConstants`, `Customer`, `ShipTo`, `Part`, `PartPlant`, `PartWhse`, `OrderHed`, `OrderDtl`, `OrderRel`, `ShipHead` (with `Weight`), `ShipDtl` (with `CustPartNum`), `InvcHead` (with `ShipToPONum_c`), `InvcDtl`.
   - [ ] Multi-company seed data loaded for `MFG01` and `MFG02`; Section 3.12 `UPDATE` statements hit existing rows (`PackNum` `50001`/`50002`, `OrderNum` `10061` lines `1`/`2`, `InvoiceNum` `90001`).
   - [ ] Verification query at end of script outputs row counts for all 14 tables without errors.

### 1.2 Execute Report Staging Procedure (`sql/02-erp-rpt-staging.sql`) and RDD Definitions (`sql/03-rdd-definitions.sql`)
1. In SSMS or via `sqlcmd`, execute `sql/02-erp-rpt-staging.sql` and `sql/03-rdd-definitions.sql`:
   ```cmd
   sqlcmd -S localhost -E -i "C:\kinetic-subcontract-lab\sql\02-erp-rpt-staging.sql"
   sqlcmd -S localhost -E -i "C:\kinetic-subcontract-lab\sql\03-rdd-definitions.sql"
   ```
2. **Verification Checklist:**
   - [ ] Database `[ErpReporting]` is created.
   - [ ] Tables `dbo.RddTable`, `dbo.RddColumn`, `dbo.RddRelationship`, and `dbo.StagedReportRun` are created in `[ErpReporting]`.
   - [ ] Stored procedures `[ErpReporting].[dbo].[usp_SetRddExclude]` and `[ErpReporting].[dbo].[usp_StageEpicorReport]` are created.
   - [ ] `dbo.usp_StageEpicorReport` dynamically builds each staged table's column list from `dbo.RddColumn WHERE Exclude = 0` using `QUOTENAME` on every column and table name.

---

## 3. Step 2: Stage Each Report Type (Base vs. Custom RDD Un-exclusions)

Execute the following T-SQL script in SSMS against database `[ErpReporting]` to stage:
1. **Base GUIDs** (with default RDD exclusions active: `CustPartNum`, `OrderNum_ProjManager_c`, `RevisionNum`, `ExtWeight`, remit-to columns, `ShipToPONum_c`, and `Weight` have `Exclude = 1`), and
2. **Custom GUIDs** (after un-excluding the lab columns via `dbo.usp_SetRddExclude` per Labs R1–R4 and R6):

```sql
USE [ErpReporting];
GO

SET NOCOUNT ON;

DECLARE @G_PackSlip_Base   NVARCHAR(36) = N'a1111111111111111111111111111100';
DECLARE @G_PackSlip_Custom NVARCHAR(36) = N'a1111111111111111111111111111101';
DECLARE @G_OrderAck_Base   NVARCHAR(36) = N'b2222222222222222222222222222200';
DECLARE @G_OrderAck_Custom NVARCHAR(36) = N'b2222222222222222222222222222202';
DECLARE @G_ARForm_Base     NVARCHAR(36) = N'c3333333333333333333333333333300';
DECLARE @G_ARForm_Custom   NVARCHAR(36) = N'c3333333333333333333333333333303';
DECLARE @G_OpenOrders      NVARCHAR(36) = N'd4444444444444444444444444444404';
DECLARE @G_R6_Fixed        NVARCHAR(36) = N'e5555555555555555555555555555505';

-- A. Stage Base Reports (with base RDD exclusions active)
-- 1. Base PackSlip (PackNum = 50001, Company = 'MFG01')
EXEC dbo.usp_StageEpicorReport
    @ReportType = N'PackSlip',
    @Company    = N'MFG01',
    @Key1       = N'50001',
    @TableGuid  = @G_PackSlip_Base OUTPUT;

-- 2. Base OrderAck (OrderNum = 10061, Company = 'MFG01' — has both Line 1 and Line 2)
EXEC dbo.usp_StageEpicorReport
    @ReportType = N'OrderAck',
    @Company    = N'MFG01',
    @Key1       = N'10061',
    @TableGuid  = @G_OrderAck_Base OUTPUT;

-- 3. Base ARForm (InvoiceNum = 90001, Company = 'MFG01')
EXEC dbo.usp_StageEpicorReport
    @ReportType = N'ARForm',
    @Company    = N'MFG01',
    @Key1       = N'90001',
    @TableGuid  = @G_ARForm_Base OUTPUT;

-- 4. OpenOrders BAQ Report (All Open Orders for Company = 'MFG01')
EXEC dbo.usp_StageEpicorReport
    @ReportType = N'OpenOrders',
    @Company    = N'MFG01',
    @Key1       = NULL,
    @TableGuid  = @G_OpenOrders OUTPUT;

-- B. Un-exclude Lab Columns via dbo.usp_SetRddExclude and Re-Stage for Custom / R6 RDLs
-- R1 & R2: Un-exclude ShipDtl.CustPartNum and ShipDtl.OrderNum_ProjManager_c
EXEC dbo.usp_SetRddExclude @RddId = N'PackSlip', @TableName = N'ShipDtl',  @ColumnName = N'CustPartNum',            @Exclude = 0;
EXEC dbo.usp_SetRddExclude @RddId = N'PackSlip', @TableName = N'ShipDtl',  @ColumnName = N'OrderNum_ProjManager_c', @Exclude = 0;
EXEC dbo.usp_StageEpicorReport
    @ReportType = N'PackSlip',
    @Company    = N'MFG01',
    @Key1       = N'50001',
    @TableGuid  = @G_PackSlip_Custom OUTPUT;

-- R6 D4: Un-exclude ShipHead.Weight and re-stage for R6_Fixed
EXEC dbo.usp_SetRddExclude @RddId = N'PackSlip', @TableName = N'ShipHead', @ColumnName = N'Weight',                 @Exclude = 0;
EXEC dbo.usp_StageEpicorReport
    @ReportType = N'PackSlip',
    @Company    = N'MFG01',
    @Key1       = N'50001',
    @TableGuid  = @G_R6_Fixed OUTPUT;

-- R3: Un-exclude OrderDtl.RevisionNum and OrderDtl.ExtWeight
EXEC dbo.usp_SetRddExclude @RddId = N'OrderAck', @TableName = N'OrderDtl', @ColumnName = N'RevisionNum',            @Exclude = 0;
EXEC dbo.usp_SetRddExclude @RddId = N'OrderAck', @TableName = N'OrderDtl', @ColumnName = N'ExtWeight',              @Exclude = 0;
EXEC dbo.usp_StageEpicorReport
    @ReportType = N'OrderAck',
    @Company    = N'MFG01',
    @Key1       = N'10061',
    @TableGuid  = @G_OrderAck_Custom OUTPUT;

-- R4: Un-exclude InvcHead Remit-To columns and ShipToPONum_c
EXEC dbo.usp_SetRddExclude @RddId = N'ARForm',   @TableName = N'InvcHead', @ColumnName = N'RemitToName',            @Exclude = 0;
EXEC dbo.usp_SetRddExclude @RddId = N'ARForm',   @TableName = N'InvcHead', @ColumnName = N'RemitToAddress1',        @Exclude = 0;
EXEC dbo.usp_SetRddExclude @RddId = N'ARForm',   @TableName = N'InvcHead', @ColumnName = N'RemitToCity',            @Exclude = 0;
EXEC dbo.usp_SetRddExclude @RddId = N'ARForm',   @TableName = N'InvcHead', @ColumnName = N'RemitToState',           @Exclude = 0;
EXEC dbo.usp_SetRddExclude @RddId = N'ARForm',   @TableName = N'InvcHead', @ColumnName = N'RemitToZip',             @Exclude = 0;
EXEC dbo.usp_SetRddExclude @RddId = N'ARForm',   @TableName = N'InvcHead', @ColumnName = N'ShipToPONum_c',          @Exclude = 0;
EXEC dbo.usp_StageEpicorReport
    @ReportType = N'ARForm',
    @Company    = N'MFG01',
    @Key1       = N'90001',
    @TableGuid  = @G_ARForm_Custom OUTPUT;

SELECT ReportType, TableGuid, Key1, StagedTables
FROM dbo.StagedReportRun
ORDER BY RunID;
GO
```

### Staging Verification Table:
Record the generated 32-hex GUID strings from your VM run:

| Report Type | Staged Test Record | Staged Tables Verified | Output TableGuid |
| :--- | :--- | :--- | :--- |
| **PackSlip (Base & Custom)** | Pack `50001` (`MFG01`) | `RptLabels_<GUID>`, `Company_<GUID>`, `ShipHead_<GUID>`, `ShipDtl_<GUID>`, `Customer_<GUID>`, `ShipTo_<GUID>` | `a1111111111111111111111111111100` / `...01` |
| **OrderAck (Base & Custom)** | Order `10061` (`MFG01`) | `RptLabels_<GUID>`, `Company_<GUID>`, `OrderHed_<GUID>`, `OrderDtl_<GUID>`, `OrderRel_<GUID>`, `Customer_<GUID>` | `b2222222222222222222222222222200` / `...02` |
| **ARForm (Base & Custom)** | Invoice `90001` (`MFG01`) | `RptLabels_<GUID>`, `Company_<GUID>`, `InvcHead_<GUID>`, `InvcDtl_<GUID>`, `Customer_<GUID>`, `ShipTo_<GUID>` | `c3333333333333333333333333333300` / `...03` |
| **OpenOrders (Base & R5)** | Open Backlog (`MFG01`) | `RptLabels_<GUID>`, `BAQReportResult_<GUID>` | `d4444444444444444444444444444404` |
| **PackSlip (R6 Fixed)** | Pack `50001` (`MFG01`) | `ShipHead_<GUID>` (with `Weight` un-excluded), `ShipDtl_<GUID>`, `Customer_<GUID>`, `ShipTo_<GUID>`, `RptLabels_<GUID>` | `e5555555555555555555555555555505` |

---

## 4. Step 3: Deploy Every RDL to SSRS 2016

### 4.1 Configure SSRS Shared Data Source
1. Open the SSRS Web Portal: `http://localhost/Reports`.
2. Create or navigate to folder `/CustomReports`.
3. Create a Shared Data Source named `ErpReportingDS`:
   - **Data Source Type**: `Microsoft SQL Server`
   - **Connection String**: `Data Source=localhost;Initial Catalog=ErpReporting;Integrated Security=True`
   - **Credentials**: `As the user viewing the report` or `Windows Integrated`.

### 4.2 Deploy RDL Files
Deploy the base RDL files (from `rdl/`), solved custom RDLs (from `answers/`), and drill RDLs to `/CustomReports`:

| # | RDL File Name | Source Location | Report Type | Version | Target SSRS Path |
|---|---------------|-----------------|-------------|---------|------------------|
| 1 | `PackSlip.rdl` | `rdl/` | PackSlip | Base | `/CustomReports/PackSlip` |
| 2 | `PackSlip_Custom.rdl` | `answers/` | PackSlip | Custom (R1, R2) | `/CustomReports/PackSlip_Custom` |
| 3 | `OrderAck.rdl` | `rdl/` | OrderAck | Base | `/CustomReports/OrderAck` |
| 4 | `OrderAck_Custom.rdl` | `answers/` | OrderAck | Custom (R3) | `/CustomReports/OrderAck_Custom` |
| 5 | `ARForm.rdl` | `rdl/` | ARForm | Base | `/CustomReports/ARForm` |
| 6 | `ARForm_Custom.rdl` | `answers/` | ARForm | Custom (R4) | `/CustomReports/ARForm_Custom` |
| 7 | `OpenOrders_Base.rdl` | `rdl/` | OpenOrders | Base | `/CustomReports/OpenOrders_Base` |
| 8 | `OpenOrders.rdl` | `answers/` | OpenOrders | Custom (R5) | `/CustomReports/OpenOrders` |
| 9 | `PackSlip_Broken.rdl` | `labs/report/R6-starter/` | PackSlip | Drill Starter (R6) | `/CustomReports/PackSlip_Broken` |
| 10 | `R6_Fixed.rdl` | `answers/` | PackSlip | Drill Solution (R6) | `/CustomReports/R6_Fixed` |

---

## 5. Step 4: Render Each RDL to PDF & Parameter Setting

Render each deployed report to PDF via SSRS URL access syntax.

### Automated PowerShell Render Script:
```powershell
# VM PDF Rendering Verification Script
$ServerUrl = "http://localhost/ReportServer"
$OutputDir = "C:\kinetic-subcontract-lab\test-pdf-output"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$Tests = @(
    @{ Name = "PackSlip";        Report = "PackSlip";        Guid = "a1111111111111111111111111111100" },
    @{ Name = "PackSlip_Custom"; Report = "PackSlip_Custom"; Guid = "a1111111111111111111111111111101" },
    @{ Name = "OrderAck";        Report = "OrderAck";        Guid = "b2222222222222222222222222222200" },
    @{ Name = "OrderAck_Custom"; Report = "OrderAck_Custom"; Guid = "b2222222222222222222222222222202" },
    @{ Name = "ARForm";          Report = "ARForm";          Guid = "c3333333333333333333333333333300" },
    @{ Name = "ARForm_Custom";   Report = "ARForm_Custom";   Guid = "c3333333333333333333333333333303" },
    @{ Name = "OpenOrders_Base"; Report = "OpenOrders_Base"; Guid = "d4444444444444444444444444444404" },
    @{ Name = "OpenOrders";      Report = "OpenOrders";      Guid = "d4444444444444444444444444444404" },
    @{ Name = "R6_Fixed";        Report = "R6_Fixed";        Guid = "e5555555555555555555555555555505" }
)

foreach ($t in $Tests) {
    $url = "$ServerUrl?/CustomReports/$($t.Report)&TableGuid=$($t.Guid)&rs:Format=PDF"
    $outFile = Join-Path $OutputDir "$($t.Name).pdf"
    Write-Host "Rendering $($t.Name) to $outFile..."
    try {
        Invoke-WebRequest -Uri $url -OutFile $outFile -UseDefaultCredentials
        Write-Host "  -> [SUCCESS] Rendered $($t.Name).pdf" -ForegroundColor Green
    } catch {
        Write-Host "  -> [FAILED] $($_.Exception.Message)" -ForegroundColor Red
    }
}
```

---

## 6. Step 5: Verification Checklist & Pass/Fail Matrix

Inspect each generated PDF on the Windows Server 2016 VM and record Pass or Fail:

| Report Name | Tested Staging Key & GUID | Required Visual Check Elements | Pass / Fail |
| :--- | :--- | :--- | :---: |
| **`PackSlip.rdl`** | Pack `50001` (`a111...00`) | Header displays Pack # `50001`, Customer `CUST01`; lines table displays `PartNum`, `LineDesc`, `SellingShippedQty`; page footer displays lab banner. | [ ] PASS<br/>[ ] FAIL |
| **`PackSlip_Custom.rdl`** | Pack `50001` (`a111...01`) | Includes **Cust Part #** (`CP-8842-A` on line 1 [R1]) and **Project Manager** (`Sarah Connor` from `OrderNum_ProjManager_c` [R2]). | [ ] PASS<br/>[ ] FAIL |
| **`OrderAck.rdl`** | Order `10061` (`b222...00`) | Header displays Order # `10061`; lines table displays both Line 1 (`PART-200`) and Line 2 (`MFG1-SPECIAL-01`). | [ ] PASS<br/>[ ] FAIL |
| **`OrderAck_Custom.rdl`** | Order `10061` (`b222...02`) | Includes **Rev** (`B` on line 1, `A` on line 2) and **Ext Weight** (`45.50` on line 1, `120.00` on line 2) [R3]. No Sync Dataset corruption. | [ ] PASS<br/>[ ] FAIL |
| **`ARForm.rdl`** | Invoice `90001` (`c333...00`) | Header displays Invoice # `90001`, Customer `CUST01`; lines table displays `ExtPrice`. | [ ] PASS<br/>[ ] FAIL |
| **`ARForm_Custom.rdl`** | Invoice `90001` (`c333...03`) | Displays boxed **Remit To** block (`ErpLab Remittance Processing, P.O. Box 75000, Chicago, IL 60675`) and **Ship-To PO #: PO-9912** (`ShipToPONum_c`) [R4]. | [ ] PASS<br/>[ ] FAIL |
| **`OpenOrders_Base.rdl`** | Open Backlog (`d444...04`) | Ungrouped base listing of open orders from `BAQReportResult_<GUID>` (`OrderHed_OrderNum`, `OrderDtl_OrderLine`, `OrderDtl_PartNum`, `OrderHed_NeedByDate`, `OrderDtl_OrderQty`, `OrderDtl_UnitPrice`). | [ ] PASS<br/>[ ] FAIL |
| **`OpenOrders.rdl`** | Open Backlog (`d444...04`) | Grouped by `Customer_CustID` with customer group headers and subtotals; displays `Calculated_DaysLate` against `FixedLabDate` (`2026-10-15`) using `OrderHed.NeedByDate`; no prompt parameters [R5]. | [ ] PASS<br/>[ ] FAIL |
| **`PackSlip_Broken.rdl`** | Pack `50001` (`a111...00`) | Expected failure before fix: fails with missing `Weight` column (`D4`), missing field references from `T1_*`/`T2_*` Sync Dataset aliases (`D1`), and `#Error` on `RowSellingShippedQty` (`D2`). | [ ] PASS (Fails as expected)<br/>[ ] FAIL |
| **`R6_Fixed.rdl`** | Pack `50001` (`e555...05`) | Renders Pack `50001` cleanly to PDF after un-excluding `ShipHead.Weight` (`D4`), restoring field names (`D1`), and fixing `RowSellingShippedQty` (`D2`). | [ ] PASS<br/>[ ] FAIL |

---

## 7. Step 6: Phase 2b BAQ Drills (`B01`–`B15` & `F01`–`F06`) Expected Results Generation & Grading against `[ErpLab]`

Expected-results CSVs must only be produced by running the answer BAQs against the real `[ErpLab]` database on the SQL Server 2016 VM.

### 7.1 First BAQ Step: Generate Expected CSVs on the VM & Commit to the Vault

After executing `sql/01-erp-app-schema.sql` in Step 1.1, run `engines/baq/make_expected.py` against `[ErpLab]` to execute all 21 answer BAQs (`B01`–`B15` and `F01`–`F06`) and write their CSV outputs into `kinetic-lab-vault/baq/expected/`, then commit and push the vault:

```powershell
$Env:BAQ_CONNECTION_STRING = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=ErpLab;Trusted_Connection=yes;"
$LabRoot   = "C:\kinetic-subcontract-lab"
$VaultRepo = "C:\kinetic-lab-vault"
$VaultRoot = "$VaultRepo\baq"

# 1. Execute all 21 answer BAQs against [ErpLab] and write expected/*.csv
python "$LabRoot\engines\baq\make_expected.py" `
    --answers-dir "$VaultRoot\answers" `
    --expected-dir "$VaultRoot\expected"

# 2. Commit and push the generated expected CSVs to kinetic-lab-vault
git -C $VaultRepo add baq/expected/*.csv
git -C $VaultRepo commit -m "Add VM-generated BAQ expected-results CSVs (B01-B15, F01-F06)"
git -C $VaultRepo push origin main
```

### 7.2 Second BAQ Step: Automated PowerShell Grader Script (Run on SQL Server 2016 VM)

Run the BAQ grader (`engines/baq/cli.py grade`) on all **21 answer BAQs** (`B01`–`B15` and `F01`–`F06`) in `kinetic-lab-vault/baq/answers/` against the generated CSVs in `kinetic-lab-vault/baq/expected/` using the live SQL Server 2016 `[ErpLab]` database. All 21 answer BAQs must exit with code `0` (`Grade: PASS`).

```powershell
$Env:BAQ_CONNECTION_STRING = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=ErpLab;Trusted_Connection=yes;"
$LabRoot   = "C:\kinetic-subcontract-lab"
$VaultRoot = "C:\kinetic-lab-vault\baq"

$Drills = @(
    "B01","B02","B03","B04","B05","B06","B07","B08","B09","B10","B11","B12","B13","B14","B15",
    "F01","F02","F03","F04","F05","F06"
)

$PassCount = 0
foreach ($id in $Drills) {
    $ansJson = Join-Path $VaultRoot "answers\$id.json"
    $expCsv  = Join-Path $VaultRoot "expected\$id.csv"
    Write-Host "Grading $id ($ansJson vs $expCsv)..."
    python "$LabRoot\engines\baq\cli.py" grade $ansJson $expCsv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  -> [PASS] $id" -ForegroundColor Green
        $PassCount++
    } else {
        Write-Host "  -> [FAIL] $id (exit code $LASTEXITCODE)" -ForegroundColor Red
    }
}
Write-Host "`nSummary: $PassCount / $($Drills.Count) BAQ Answer Drills Passed."
```

### 7.3 BAQ Grader Verification Matrix (Expect All 21 Answers to PASS)

| Drill ID | BAQ ID | Category | Answer BAQ & Expected CSV (`kinetic-lab-vault/baq/`) | Expected Rows | Expected Result | Pass / Fail |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **`B01`** | `BAQ_B01_CustDirectory` | Single-Table | `answers/B01.json` vs `expected/B01.csv` | 21 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B02`** | `BAQ_B02_PPAPParts` | Single-Table | `answers/B02.json` vs `expected/B02.csv` | 4 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B03`** | `BAQ_B03_OpenOrdersWindow` | Single-Table | `answers/B03.json` vs `expected/B03.csv` | 10 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B04`** | `BAQ_B04_ShipmentManifest` | Single-Table | `answers/B04.json` vs `expected/B04.csv` | 10 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B05`** | `BAQ_B05_OrdersWithCustomer` | Joins | `answers/B05.json` vs `expected/B05.csv` | 15 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B06`** | `BAQ_B06_CustomerShipToSites` | Joins | `answers/B06.json` vs `expected/B06.csv` | 12 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B07`** | `BAQ_B07_OrderLinePartSpecs` | Joins | `answers/B07.json` vs `expected/B07.csv` | 10 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B08`** | `BAQ_B08_PackSlipLines` | Joins | `answers/B08.json` vs `expected/B08.csv` | 5 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B09`** | `BAQ_B09_InvoiceRegister` | Joins | `answers/B09.json` vs `expected/B09.csv` | 5 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B10`** | `BAQ_B10_LineExtendedPrice` | Calculated Fields | `answers/B10.json` vs `expected/B10.csv` | 10 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B11`** | `BAQ_B11_LateOrderAging` | Calculated Fields | `answers/B11.json` vs `expected/B11.csv` | 15 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B12`** | `BAQ_B12_OrderValueTier` | Calculated Fields | `answers/B12.json` vs `expected/B12.csv` | 16 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B13`** | `BAQ_B13_ShipmentFillRatio` | Calculated Fields | `answers/B13.json` vs `expected/B13.csv` | 9 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B14`** | `BAQ_B14_PartOnHandSummary` | `InnerSubQuery` | `answers/B14.json` vs `expected/B14.csv` | 7 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`B15`** | `BAQ_B15_CustomerOpenBacklog` | `InnerSubQuery` | `answers/B15.json` vs `expected/B15.csv` | 10 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`F01`** | `BAQ_F01_CustomerOrders` | Fix Drill | `answers/F01.json` vs `expected/F01.csv` | 10 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`F02`** | `BAQ_F02_RegionalAccountOrders` | Fix Drill | `answers/F02.json` vs `expected/F02.csv` | 12 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`F03`** | `BAQ_F03_StaggeredLineSchedule` | Fix Drill | `answers/F03.json` vs `expected/F03.csv` | 10 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`F04`** | `BAQ_F04_OpenOrdersWithReleases` | Fix Drill | `answers/F04.json` vs `expected/F04.csv` | 5 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`F05`** | `BAQ_F05_LateBacklogAging` | Fix Drill | `answers/F05.json` vs `expected/F05.csv` | 15 | `Grade: PASS` | [ ] PASS / [ ] FAIL |
| **`F06`** | `BAQ_F06_OrderReleaseFulfillment` | Fix Drill | `answers/F06.json` vs `expected/F06.csv` | 20 | `Grade: PASS` | [ ] PASS / [ ] FAIL |

---

## 8. Sign-Off & Environmental Certification

- **VM Tester Name**: `____________________________________`
- **Execution Date**: `____________________________________`
- **Result Summary**: `10 of 10 RDLs Verified; 21 of 21 BAQ Answer Drills Passed`
- **Notes / Observations**:
