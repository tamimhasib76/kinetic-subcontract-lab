# Lab R6: PackSlip — Troubleshooting & Recovery Drill (Five Planted Faults)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-RPT-106` |
| **Client** | MFG01 Manufacturing Corp |
| **Report / Form** | Packing Slip (`PackSlip`) |
| **Environment** | Windows Server 2016 / SQL Server 2016 / SSRS 2016 (`[ErpLab]` & `[ErpReporting]`) |
| **Priority** | Critical (Production Down) |
| **Summary** | Shipping clerks at MFG01 cannot print Packing Slips. A contractor attempted to customize `PackSlip` directly on the system yesterday, clicked **Sync Dataset** (`[S24, S25]`), edited a textbox expression, added `T1.Weight` to the RDL without un-excluding it in the RDD (`[S14]`), and misconfigured Report Style. Diagnose and repair all **five planted defects** (`D1`–`D5`) so Packing Slips render cleanly to PDF. |

### Starter Files & Scenario Context
- **Starter Broken RDL (File Defects `D1`, `D2`, `D4`)**: Start from [`labs/report/R6-starter/PackSlip_Broken.rdl`](R6-starter/PackSlip_Broken.rdl), which contains the three RDL-level faults planted in the file.
- **Report Style Configuration Scenario (Non-File Defects `D3`, `D5`)**: In addition to the broken RDL file, the contractor left two configuration defects in **Report Style**:
  1. **Scenario Defect `D5` (Edited System Style)**: Instead of copying the system style via **Copy Report Style** (`[S1, S5, S9]`, §1.1–§1.4; `Generate for Design` is greyed out on a system style `[S1]`, §1.2), the contractor edited the out-of-the-box **`Standard - SSRS`** style (`reports/StandardReports/PackingSlip/PackSlip` — *Default chosen for the lab, not confirmed against Epicor*) directly.
  2. **Scenario Defect `D3` (Wrong Report Location Path)**: When attempting to move the report, the contractor entered a broken path (`/CustomReports/PackSlip/PackSlip_Broken.rdl`) into **Report Location**, causing Report Style upload to fail with **`"Could not find a part of the path"`** (`[S6]`, [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §7.10).

### Summary of All Five Planted Defects (`D1`–`D5`)

| Defect ID | Category | Where Planted | Symptom / Error | Reference Citation |
|---|---|---|---|---|
| **`D1`** | **Sync Dataset Damage** | [`labs/report/R6-starter/PackSlip_Broken.rdl`](R6-starter/PackSlip_Broken.rdl) (`<CommandText>` & `<Fields>`) | Contractor clicked **Sync Dataset**, which rewrote the dataset query aliases and `<Field>` names to `T1_PackNum`, `T2_PartNum`, etc. (*alias prefix pattern: Default chosen for the lab, not confirmed against Epicor*), while the report tablix and header textboxes still reference `Fields!PackNum.Value`, `Fields!PartNum.Value`, etc., failing RDL compilation (`The Value expression for the textrun ... refers to a non-existing reportitem or field`) | [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §8.1–§8.2 & §8.5 (`[S24, S25]`) |
| **`D2`** | **Wrong Field Expression Type (`#Error` at Render)** | [`labs/report/R6-starter/PackSlip_Broken.rdl`](R6-starter/PackSlip_Broken.rdl) (`<Textbox Name="RowSellingShippedQty">`) | Contractor wrapped `Fields!SellingShippedQty.Value` (`DECIMAL(15,4)`) inside a date function (`=Format(DateAdd("d", 1, Fields!SellingShippedQty.Value), "yyyy-MM-dd")`), causing the **Shipped Qty** column to render **`#Error`** at runtime | *Default chosen for the lab, not confirmed against Epicor* |
| **`D3`** | **Wrong Report Location** | Scenario text (Report Style **Report Location**) | **Report Location** had a path problem (`/CustomReports/PackSlip/PackSlip_Broken.rdl`), triggering **`"Could not find a part of the path"`** | [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §2.1–§2.3 (`[S3, S5]`) & §7.10 (`[S6]`) |
| **`D4`** | **Field Excluded in RDD (`ShipHead.Weight`)** | [`labs/report/R6-starter/PackSlip_Broken.rdl`](R6-starter/PackSlip_Broken.rdl) (`T1.Weight`) + `ErpReporting.dbo.RddColumn` | Dataset query selects `T1.Weight` from `dbo.[ShipHead_<GUID>]`, but `Weight` has `Exclude = 1` in the base `PackSlip` RDD (`dbo.RddColumn`), so `dbo.[ShipHead_<GUID>]` does not contain `Weight` (`Invalid column name 'Weight'`) until `ShipHead.Weight` is un-excluded and re-staged | [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.4–§3.7 (`[S12, S13, S14, S25]`); Approved Default 20 |
| **`D5`** | **Edited System Style** | Scenario text (Report Style **`Standard - SSRS`**) | Contractor modified the system **`Standard - SSRS`** style directly instead of copying to a custom style | [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §1.1–§1.4 (`[S1, S5, S9]`) |

> **Banners & Citations**
> - **Never Click Sync Dataset & Manual RDL Editing**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §8.1–§8.2 & §8.5 (`[S24, S25]`).
> - **Report Location Path Format & Error Message**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §2.1–§2.3 (`[S3, S5]`) and §7.10 (`"Could not find a part of the path"` `[S6]`).
> - **RDD Exclusions Control Staging Table Columns**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.4–§3.7 (`[S12, S13, S14, S25]`).
> - **Lab Design (Approved Default 20, [`docs/reference/decisions.md`](../../docs/reference/decisions.md))**: Un-excluding `ShipHead.Weight` via `dbo.usp_SetRddExclude` affects only subsequent `dbo.usp_StageEpicorReport` runs.
> - **Default chosen for the lab, not confirmed against Epicor**: The factory path `reports/StandardReports/PackingSlip/PackSlip`, the lab custom path `reports/CustomReports/PackingSlip/PackSlip_Custom`, the specific `T1_*` / `T2_*` alias prefix pattern used in `PackSlip_Broken.rdl` to simulate Sync Dataset field-name changes (`[S25]`), the planted `DateAdd` expression fault (`D2`), custom RDD code `PackSlip_Custom`, Copy Report Style dialog field values (such as style number `1002`), shared data source `ErpReportingDS`, and the SQL stand-in procedure `dbo.usp_SetRddExclude`.

---

## Step-by-Step Resolution Guide

### Step 1: Remediate `D5` (Edited System Style) and `D3` (Wrong Report Location)
1. Open **Report Style** and load Report ID **`PackSlip`** (`[S1, S5]`, §1.1, §1.3).
2. **Fix `D5`**: Restore the system **`Standard - SSRS`** style (`[S1]`, §1.2) to its factory defaults (`Data Definition = PackSlip`, `Report Location = reports/StandardReports/PackingSlip/PackSlip` — *factory path: Default chosen for the lab, not confirmed against Epicor*).
3. Select **`Standard - SSRS`** and copy the style via **Copy Report Style** (`[S1, S5, S9]`, §1.1–§1.4) to create a dedicated custom style (for example, Style `1002` — *Default chosen for the lab, not confirmed against Epicor*).
4. **Fix `D3`**: In Report Style, a path problem in **Report Location** causes **`"Could not find a part of the path"`** (`[S6]`, `01-ssrs-forms.md` §7.10). Custom styles place reports under `reports/CustomReports/...` (`[S3, S5]`, §2.1–§2.3; whether `Report Location` includes the `.rdl` filename is open in the reference — `[S5]` shows it included, `[S3]` shows `reports/CustomReports/xxx` — so match the client's existing style `[S5, S32]`, §2.3, §7.3). For this lab, set **Report Location** on your custom style to (*Default chosen for the lab, not confirmed against Epicor*):
   ```text
   reports/CustomReports/PackingSlip/PackSlip_Custom
   ```
   and assign your duplicated RDD **`PackSlip_Custom`** in the style's **Data Definition** field (`[S15]`, §1.8; *`PackSlip_Custom` name: Default chosen for the lab, not confirmed against Epicor*). Save the style.

### Step 2: Remediate `D4` (Un-exclude `ShipHead.Weight` in the RDD and Re-Stage)
1. Inspect [`labs/report/R6-starter/PackSlip_Broken.rdl`](R6-starter/PackSlip_Broken.rdl) and observe that the `SELECT` clause queries `T1.Weight` from `dbo.[ShipHead_" + Parameters!TableGuid.Value + "] T1` (`[S13, S14, S19]`, Explicit Answer 1 & 5).
2. Check [`engines/report/PackSlip.json`](../../engines/report/PackSlip.json) and `ErpReporting.dbo.RddColumn`: `Weight` on `ShipHead` has **`Exclude = 1`** in the base `PackSlip` RDD! Because the staging table's columns are set by the exclusions in the RDD (`[S14]`, §3.6), staging `PackSlip` while `ShipHead.Weight` is excluded omits `[Weight]` from `dbo.[ShipHead_<GUID>]`, and running the report fails with `Invalid column name 'Weight'`.
3. **Fix `D4`**: In **Report Data Definition** on your duplicated RDD **`PackSlip_Custom`** (`[S15]`, §3.1), select the **`ShipHead`** table, open the **Exclusions** tab (`[S12]`, §3.4), clear the **Exclude** checkbox for **`Weight`** (`[S12, S25]`, §3.5), and save.
   - **Lab SQL Stand-In** (*Default chosen for the lab, not confirmed against Epicor*): In SSMS against `[ErpReporting]`, un-exclude `ShipHead.Weight` via `dbo.usp_SetRddExclude`:
     ```sql
     USE [ErpReporting];
     EXEC dbo.usp_SetRddExclude
         @RddId      = N'PackSlip',
         @TableName  = N'ShipHead',
         @ColumnName = N'Weight',
         @Exclude    = 0;
     ```
4. Now **re-stage** `PackSlip` (`Company = 'MFG01'`, `Key1 = '50001'`) so the newly staged `dbo.[ShipHead_<GUID>]` table includes the `[Weight]` column (`48.5000` on `PackNum = 50001`, per `[S14]` and Approved Default 20):
   ```sql
   USE [ErpReporting];
   DECLARE @Guid NVARCHAR(36) = N'e5555555555555555555555555555505';
   EXEC dbo.usp_StageEpicorReport
       @ReportType = N'PackSlip',
       @Company    = N'MFG01',
       @Key1       = N'50001',
       @TableGuid  = @Guid OUTPUT;
   SELECT @Guid AS StagedTableGuid;
   ```

### Step 3: Remediate `D1` (Sync Dataset Field-Name Damage)
1. Open a working copy of [`labs/report/R6-starter/PackSlip_Broken.rdl`](R6-starter/PackSlip_Broken.rdl) in **Report Builder** (or an XML editor) (`[S2]`, §7.4).
2. Inspect the `PackSlip` dataset `<CommandText>` and `<Fields>` collection:
   - The query aliases `ShipHead` and `ShipDtl` columns as `T1_Company`, `T1_PackNum`, `T1_ShipDate`, `T1_TrackingNumber`, `T1_ShipViaCode`, `T1_Weight`, `T2_PackLine`, `T2_OrderNum`, `T2_OrderLine`, `T2_OrderRelNum`, `T2_PartNum`, `T2_LineDesc`, `T2_SellingShippedQty`, `T2_SalesUM`, and the `<Fields>` collection defines `<Field Name="T1_PackNum">`, `<Field Name="T2_PartNum">`, etc. (*`T1_*`/`T2_*` alias pattern: Default chosen for the lab, not confirmed against Epicor*).
   - Meanwhile, the report body textboxes (`HeaderPackNum`) and `PackLinesTablix` cells (`RowPackLine`, `RowPartNum`, `RowLineDesc`, `RowSellingShippedQty`) reference `Fields!PackNum.Value`, `Fields!PackLine.Value`, `Fields!PartNum.Value`, `Fields!LineDesc.Value`, and `Fields!SellingShippedQty.Value` (`[S25]`, §8.2).
3. **Fix `D1`**: Manually restore the clean `SELECT` column names in `<CommandText>` (removing the `T1_*` and `T2_*` aliases while keeping `T1.Weight`) and restore the `<Field Name="...">` / `<DataField>...</DataField>` entries (`Company`, `PackNum`, `ShipDate`, `TrackingNumber`, `ShipViaCode`, `Weight`, `PackLine`, `OrderNum`, `OrderLine`, `OrderRelNum`, `PartNum`, `LineDesc`, `SellingShippedQty`, `SalesUM`) in **Dataset Properties** (`[S24, S25]`, §8.5).

### Step 4: Remediate `D2` (Fix `#Error` Date-Function Expression on `SellingShippedQty`)
1. In [`labs/report/R6-starter/PackSlip_Broken.rdl`](R6-starter/PackSlip_Broken.rdl), inspect `<Textbox Name="RowSellingShippedQty">` inside `PackLinesTablix`:
   ```xml
   <Value>=Format(DateAdd("d", 1, Fields!SellingShippedQty.Value), "yyyy-MM-dd")</Value>
   ```
   Because `SellingShippedQty` is a `DECIMAL(15, 4)` (`System.Decimal`), passing it to `DateAdd("d", 1, ...)` (*planted expression fault: Default chosen for the lab, not confirmed against Epicor*) causes SSRS to evaluate a runtime type error and display **`#Error`** in the **Shipped Qty** column when rendered!
2. **Fix `D2`**: Change the `<Textbox Name="RowSellingShippedQty">` expression back to:
   ```xml
   <Value>=Fields!SellingShippedQty.Value</Value>
   ```
   with `<Format>N2</Format>`.
3. Preview the repaired report in Report Builder with `TableGuid = e5555555555555555555555555555505` (`[S21]`, §5.4; `Company = 'MFG01'`, `PackNum = '50001'`) and verify that the report renders cleanly with `10.00` in **Shipped Qty** and zero `#Error` cells.
4. Save the repaired RDL file (`[S2]`, §7.4).

### Step 5: Upload, Re-Download, and Confirm Round-Trip Integrity
1. In **Report Style**, select your custom `PackSlip` style (`reports/CustomReports/PackingSlip/PackSlip_Custom`) and upload the RDL via the overflow (three-dot) menu > **Upload SSRS Report** (`[S32, S2]`, §7.7) or in Classic via **Action > Upload SSRS report** (`[S3, S6]`, §7.16).
2. Immediately re-download the report from Report Style via **Download SSRS Report** (`[S32, S8]`, §7.1; Classic **Actions > Download SSRS Report** `[S3]`, §7.14) into a verification folder.
3. **Mandatory Verification (Lab Rule, [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §7c, motivated by `[S1, S8, S9, S11]`)**: Re-download from Report Style and confirm the changes (restored `<CommandText>` and `<Fields>` including `Weight`, and `=Fields!SellingShippedQty.Value` on `RowSellingShippedQty`) are in the file.
