# Lab R1: PackSlip — Add Excluded Column (`CustPartNum`) from Existing Table

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-RPT-101` |
| **Client** | MFG01 Manufacturing Corp |
| **Report / Form** | Packing Slip (`PackSlip`) |
| **Environment** | Windows Server 2016 / SQL Server 2016 / SSRS 2016 (`[ErpLab]` & `[ErpReporting]`) |
| **Priority** | Medium |
| **Summary** | Receiving clerks at Customer `CUST01` require their own **Customer Part Number** (`CustPartNum`) printed next to our internal `PartNum` on the Packing Slip (`PackSlip`). The column already exists on `Erp.ShipDtl`, but it is excluded by default in the base `PackSlip` Report Data Definition (RDD). |

### Acceptance Criteria
1. Duplicate the system `PackSlip` RDD (`[S15]`) and un-exclude `CustPartNum` on `ShipDtl` (`[S12, S25]`; in the lab SQL environment, run `dbo.usp_SetRddExclude` so `ErpReporting.dbo.RddColumn` has `Exclude = 0` for `ShipDtl.CustPartNum`).
2. Copy the system `PackSlip` Report Style (`[S1, S5, S9]`) to a custom style pointing to your custom RDD (`[S15]`) and custom `Report Location` (`[S3, S5]`), never modifying the system style (`[S1, S9]`).
3. Start from the base [`rdl/PackSlip.rdl`](../../rdl/PackSlip.rdl), add `T2.CustPartNum` (and `T5.LblCustPartNum`) to the `PackSlip` dataset query expression and `<Fields>` collection without using **Sync Dataset** (`[S24, S25]`), and place `CustPartNum` on the line items table.
4. Upload/deploy the updated RDL (`[S32, S2, S3, S6]`), re-download it from Report Style (`[S32, S8, S3]`), and confirm your changes are present in the re-downloaded file.

> **Banners & Citations**
> - **RDD Duplication & Un-excluding Columns**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.1 (`[S15]`) and §3.4–§3.7 (`[S12, S13, S14, S25]`).
> - **Report Style Copy & Custom Path**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §1.1–§1.4 (`[S1, S5, S9]`), §1.8 (`[S15]`), and §2.1–§2.3 (`[S3, S5]`).
> - **Staging Tables, Archive Period & Manual RDL Editing (No Sync Dataset)**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) Explicit Answer 1 & 5 (`[S13, S14, S19, S8]`), §5.4 (`[S21]`), §7.4 (`[S2]`), and §8.1–§8.2 & §8.5 (`[S24, S25]`).
> - **Round-Trip Upload & Re-download Verification**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §7.1 & §7.7 (`[S32, S8, S2]`), §7.14 & §7.16 (`[S3, S6]`), and §7c (lab rule motivated by `[S1, S8, S9, S11]`).
> - **Lab Design (Approved Default 20, [`docs/reference/decisions.md`](../../docs/reference/decisions.md))**: Un-excluding a column in `ErpReporting.dbo.RddColumn` via `dbo.usp_SetRddExclude` affects only subsequent `dbo.usp_StageEpicorReport` runs; previously staged `<Table>_<GUID>` tables are not altered retroactively.
> - **Default chosen for the lab, not confirmed against Epicor**: Custom RDD code `PackSlip_Custom`, the `"System is checked"` indicator, the `"Actions > Duplicate Report"` menu label, the `"Exclude Label"` checkbox, Copy Report Style dialog field values (such as style number `1001`), the lab `Report Location` path `reports/CustomReports/PackingSlip/PackSlip_Custom`, label column `LblCustPartNum`, Report Builder dialog button labels (`fx`, `Add > Query Field`), shared data source `ErpReportingDS`, and the SQL stand-in procedure `dbo.usp_SetRddExclude`.

---

## Step-by-Step Guide

### Step 1: Duplicate the System RDD and Un-exclude `CustPartNum`
1. Open **Report Data Definition** and load the **`PackSlip`** definition.
2. Confirm that **System is checked** on the standard definition (*Default chosen for the lab, not confirmed against Epicor*). Duplicate the RDD and edit the copy, not the base (`[S15]`, §3.1): select **Actions > Duplicate Report** (*Default chosen for the lab, not confirmed against Epicor*) and save the copy as **`PackSlip_Custom`** (*Default chosen for the lab, not confirmed against Epicor*).
3. In `PackSlip_Custom`, select the **`ShipDtl`** table and open the **Exclusions** tab (`[S12]`, §3.4).
4. Locate **`CustPartNum`** (and `LblCustPartNum` in `RptLabels` if excluded), clear its **Exclude** checkbox (`[S12, S25]`, §3.5) (and verify **Exclude Label** is unchecked if you need the translated label — *Default chosen for the lab, not confirmed against Epicor*), and save. The temp (staging) table's columns are set by the exclusions in the RDD (`[S14]`, §3.6), and any field shown on the report or used in an expression must stay included (`[S13]`, §3.7).
   - **Lab SQL Stand-In** (*Default chosen for the lab, not confirmed against Epicor*): In SQL Server Management Studio (SSMS) against `[ErpReporting]`, inspect `dbo.RddColumn` and un-exclude `ShipDtl.CustPartNum`:
     ```sql
     USE [ErpReporting];
     EXEC dbo.usp_SetRddExclude
         @RddId      = N'PackSlip',
         @TableName  = N'ShipDtl',
         @ColumnName = N'CustPartNum',
         @Exclude    = 0;
     ```
5. Reference: [`engines/report/PackSlip.json`](../../engines/report/PackSlip.json) and [`sql/03-rdd-definitions.sql`](../../sql/03-rdd-definitions.sql) define `CustPartNum` on `ShipDtl` with `Exclude = 1` in the base RDD.

### Step 2: Copy the System Report Style (Never Edit the System Style)
1. Open **Report Style** for **`PackSlip`** (`[S1, S5]`, §1.1, §1.3).
2. Select the system style **`Standard - SSRS`** and copy it via the overflow menu > **Copy Report Style** (`[S1, S5]`, §1.1–§1.3).
   - **Rule**: You cannot design a system style directly (`Generate for Design` is greyed out on a system style `[S1]`, §1.2); always start from a copy of the out-of-box style (`[S9]`, §1.4).
3. On the new custom style (for example, Style `1001` — *Default chosen for the lab, not confirmed against Epicor*):
   - Assign the duplicated RDD **`PackSlip_Custom`** in the style's **Data Definition** field (`[S15]`, §1.8).
   - Set **Report Location** under `reports/CustomReports/...` (`[S3, S5]`, §2.1–§2.3). Whether **Report Location** includes the `.rdl` filename is open in the reference (`[S5]` §2.2–§2.3 shows `.rdl` included, whereas `[S3]` §2.1 shows `reports/CustomReports/xxx`); in a client environment, **match the client's existing style** (`[S5, S32]`, §2.3, §7.3). For this lab, we use `reports/CustomReports/PackingSlip/PackSlip_Custom` (*Default chosen for the lab, not confirmed against Epicor*).
4. Save the Report Style.

### Step 3: Stage Test Data and Download the Base RDL
1. In Epicor, download the SSRS report from your copied style using the overflow (three-dot) menu > **Download SSRS Report** (`[S32, S8]`, §7.1) or in Classic Report Style Maintenance via **Actions > Download SSRS Report** (`[S3]`, §7.14). When running the report to stage test data, set **Archive Period** = **Day**, copy the GUID from the System Monitor **Reports** tab, and paste it into the **`TableGuid`** parameter in Report Builder (`[S21]`, §5.4; with Archive Period = 0 days, GUID tables disappear after ~1 minute `[S23]`, §5.5).
2. In the lab SQL environment, start from the base [`rdl/PackSlip.rdl`](../../rdl/PackSlip.rdl) and stage a Packing Slip test dataset in `[ErpReporting]` for `Company = 'MFG01'`, `PackNum = '50001'` (where `Erp.ShipDtl` has `CustPartNum = 'CP-8842-A'` on `PackLine = 1`):
   ```sql
   USE [ErpReporting];
   DECLARE @Guid NVARCHAR(36) = N'a1111111111111111111111111111101';
   EXEC dbo.usp_StageEpicorReport
       @ReportType = N'PackSlip',
       @Company    = N'MFG01',
       @Key1       = N'50001',
       @TableGuid  = @Guid OUTPUT;
   SELECT @Guid AS StagedTableGuid;
   ```
   Because you ran `dbo.usp_SetRddExclude` in Step 1 before staging, `dbo.[ShipDtl_a1111111111111111111111111111101]` now includes the `[CustPartNum]` column (`[S14]`, Approved Default 20).

### Step 4: Modify the Dataset Query Expression and `<Fields>` Manually in Report Builder
1. Open your working copy of [`rdl/PackSlip.rdl`](../../rdl/PackSlip.rdl) in **Report Builder** (`[S2]`, §7.4).
2. **Do NOT click Sync Dataset** on standard Epicor reports (`[S24, S25]`, §8.1–§8.2). Instead, add the un-excluded field manually to the dataset query `SELECT` and to the dataset **Fields** list in Report Builder (`[S24, S25]`, §8.5).
3. Open **Dataset Properties** for the **`PackSlip`** dataset (`[S24, S25]`, §8.5) and open the query expression (`fx` — *Default chosen for the lab, not confirmed against Epicor*).
4. Locate the `SELECT` clause where `ShipDtl_<GUID>` (`T2`) and `RptLabels_<GUID>` (`T5`) columns are selected via `Parameters!TableGuid.Value` (`[S13, S14, S19, S8]`, Explicit Answers 1 & 5), and add **`T2.CustPartNum`** and **`T5.LblCustPartNum`** (`[S24, S25]`, §8.5):
   ```vb
   + "T2.PackLine, T2.OrderNum, T2.OrderLine, T2.OrderRelNum, T2.PartNum, T2.LineDesc, "
   + "T2.CustPartNum, T2.SellingShippedQty, T2.SalesUM, "
   ```
   and in the `T5` label list:
   ```vb
   + "T5.LblPartNum, T5.LblLineDesc, T5.LblCustPartNum, T5.LblShipQty "
   ```
   *(Note: `LblCustPartNum` in `RptLabels_<GUID>` is a lab default — Default chosen for the lab, not confirmed against Epicor.)*
5. Click **OK** on the Query screen, switch to the **Fields** list in **Dataset Properties** (`[S24, S25]`, §8.5), and add (`Add > Query Field` — *Default chosen for the lab, not confirmed against Epicor*):
   - **Field Name**: `CustPartNum` | **Field Source**: `CustPartNum` (`System.String`)
   - **Field Name**: `LblCustPartNum` | **Field Source**: `LblCustPartNum` (`System.String`)
6. Click **OK** on Dataset Properties (`[S24, S25]`, §8.5).

### Step 5: Add the Column to the Tablix and Preview with `TableGuid`
1. On the report design surface, right-click the `PartNum` column header in `PackLinesTablix` and choose **Insert Column > Right**.
2. Set the header cell expression to `=First(Fields!LblCustPartNum.Value, "PackSlip")` (or static text `"Cust Part #"`).
3. Set the detail row cell expression to `=Fields!CustPartNum.Value`.
4. Preview the report in Report Builder, paste `a1111111111111111111111111111101` into the **`TableGuid`** parameter (`[S21]`, §5.4), and verify that `CP-8842-A` renders on `PackNum` `50001` Line `1`.
5. Save the RDL file (`[S2]`, §7.4).

### Step 6: Upload, Re-Download, and Confirm Round-Trip Integrity
1. In **Report Style**, select your custom `PackSlip` style and upload the RDL via the overflow (three-dot) menu > **Upload SSRS Report** (`[S32, S2]`, §7.7) or in Classic via **Action > Upload SSRS report** (`[S3, S6]`, §7.16) (or deploy to the SSRS 2016 folder `/CustomReports/PackingSlip` on the lab VM).
2. Immediately re-download the report from Report Style via **Download SSRS Report** (`[S32, S8]`, §7.1; Classic **Actions > Download SSRS Report** `[S3]`, §7.14) into a new verification directory.
3. **Mandatory Verification (Lab Rule, [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §7c, motivated by `[S1, S8, S9, S11]`)**: Re-download from Report Style and confirm the change (`T2.CustPartNum`, `<Field Name="CustPartNum">`, and the tablix cell `=Fields!CustPartNum.Value`) is present in the downloaded `.rdl` file before closing the ticket.
