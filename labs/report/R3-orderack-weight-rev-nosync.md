# Lab R3: OrderAck — Add Extended Weight & Revision Number (Without Sync Dataset)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-RPT-103` |
| **Client** | MFG01 Manufacturing Corp |
| **Report / Form** | Sales Order Acknowledgment (`OrderAck`) (`[S1, S24, S33]`) |
| **Environment** | Windows Server 2016 / SQL Server 2016 / SSRS 2016 (`[ErpLab]` & `[ErpReporting]`) |
| **Priority** | High |
| **Summary** | Engineering and logistics require **Revision Number** (`RevisionNum`) and **Extended Weight** (`ExtWeight`) printed on every line of the Sales Order Acknowledgment (`OrderAck`). Both columns exist on `Erp.OrderDtl` but are excluded in the base `OrderAck` RDD. A junior developer previously clicked **Sync Dataset** on `OrderAck` in test and broke the report (`[S24, S25]`). Rebuild the customization cleanly **without** touching Sync Dataset. |

### Acceptance Criteria
1. Duplicate the `OrderAck` RDD (`[S15]`) and un-exclude `RevisionNum` and `ExtWeight` on `OrderDtl` (`[S12, S25]`; in the lab SQL environment, un-exclude both columns via `dbo.usp_SetRddExclude`).
2. Create a custom Report Style for `OrderAck` (`[S1, S5, S9, S15]`) without ever clicking **Sync Dataset** (`[S24, S25]`).
3. Starting from the base [`rdl/OrderAck.rdl`](../../rdl/OrderAck.rdl), manually edit the `OrderAck` dataset query expression and `<Fields>` collection to add `T2.RevisionNum` and `T2.ExtWeight` (plus labels `T5.LblRevisionNum` and `T5.LblExtWeight`) (`[S24, S25]`), and add both columns to the line items tablix.
4. Upload (`[S32, S2, S3, S6]`), re-download from Report Style (`[S32, S8, S3]`), and confirm the change is in the file.

> **Banners & Citations**
> - **Why Never to Click Sync Dataset & Manual RDL Alternative**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §8.1–§8.2 & §8.5 (`[S24, S25]`).
> - **RDD Duplication & Column Un-exclusion**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.1 (`[S15]`) and §3.4–§3.7 (`[S12, S13, S14, S25]`).
> - **Report Style Copy & Custom Path**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §1.1–§1.4 (`[S1, S5, S9]`), §1.8 (`[S15]`), and §2.1–§2.3 (`[S3, S5]`).
> - **Lab Design (Approved Default 20, [`docs/reference/decisions.md`](../../docs/reference/decisions.md))**: Un-excluding `RevisionNum` and `ExtWeight` via `dbo.usp_SetRddExclude` affects only subsequent `dbo.usp_StageEpicorReport` runs.
> - **Default chosen for the lab, not confirmed against Epicor**: Custom RDD code `OrderAck_Custom`, the `"Actions > Duplicate Report"` menu label, Copy Report Style dialog field values (such as style number `1001`), the lab `Report Location` path `reports/CustomReports/SalesOrderAcknowledgement/OrderAck_Custom`, label column names `LblRevisionNum` and `LblExtWeight` in `RptLabels_<GUID>`, Report Builder dialog button labels (`fx`, `Add > Query Field`), shared data source `ErpReportingDS`, and the SQL stand-in procedure `dbo.usp_SetRddExclude`.

---

## Step-by-Step Guide

### Step 1: Duplicate `OrderAck` RDD and Un-exclude `RevisionNum` and `ExtWeight`
1. Open **Report Data Definition**, load **`OrderAck`**, and duplicate the RDD (`[S15]`, §3.1) via **Actions > Duplicate Report** (*Default chosen for the lab, not confirmed against Epicor*) to create **`OrderAck_Custom`** (*Default chosen for the lab, not confirmed against Epicor*).
2. Select **`OrderDtl`** and open the **Exclusions** tab (`[S12]`, §3.4).
3. Locate **`RevisionNum`** and **`ExtWeight`**, clear the **Exclude** checkbox on both rows (`[S12, S25]`, §3.5), and save. The staging table's columns are set by the exclusions in the RDD (`[S14]`, §3.6).
   - **Lab SQL Stand-In** (*Default chosen for the lab, not confirmed against Epicor*): In SSMS against `[ErpReporting]`, un-exclude both columns on `OrderDtl`:
     ```sql
     USE [ErpReporting];
     EXEC dbo.usp_SetRddExclude
         @RddId      = N'OrderAck',
         @TableName  = N'OrderDtl',
         @ColumnName = N'RevisionNum',
         @Exclude    = 0;

     EXEC dbo.usp_SetRddExclude
         @RddId      = N'OrderAck',
         @TableName  = N'OrderDtl',
         @ColumnName = N'ExtWeight',
         @Exclude    = 0;
     ```
4. Reference: [`engines/report/OrderAck.json`](../../engines/report/OrderAck.json) and [`sql/03-rdd-definitions.sql`](../../sql/03-rdd-definitions.sql) define `RevisionNum` and `ExtWeight` on `OrderDtl` with `Exclude = 1` in the base RDD.

### Step 2: Copy the `OrderAck` Report Style (Do NOT Click Sync Dataset)
1. Open **Report Style**, load Report ID **`OrderAck`** (`[S1, S24, S33]`), select **`Standard - SSRS`**, and copy the style via **Copy Report Style** (`[S1, S5, S9]`, §1.1–§1.4).
2. Assign **`OrderAck_Custom`** in the style's **Data Definition** field (`[S15]`, §1.8) and set **Report Location** under `reports/CustomReports/...` (`[S3, S5]`, §2.1–§2.3; match the client's existing style on whether `.rdl` is included `[S5, S32]`; for this lab we use `reports/CustomReports/SalesOrderAcknowledgement/OrderAck_Custom` — *Default chosen for the lab, not confirmed against Epicor*).
3. **CRITICAL RULE**: Do **NOT** click **Sync Dataset** on standard Epicor reports (`[S24, S25]`, §8.1–§8.2).
   - Practitioner guidance in [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §8.1–§8.2 warns not to use **Sync Dataset** on standard Epicor reports like `OrderAck` because it will *"pollute"* the report *"to where you will not be able to run it"* (`[S24]`), altering dataset structure, changing field names, and breaking dataset queries (`[S25]`).

### Step 3: Stage Test Data for `OrderAck` (`OrderNum = 10061`)
1. In Epicor, run the report with **Archive Period** = **Day**, copy the GUID from the System Monitor **Reports** tab, and paste it into the **`TableGuid`** parameter in Report Builder (`[S21]`, §5.4).
2. In the lab SQL environment, run `dbo.usp_StageEpicorReport` for `OrderAck` (`Company = 'MFG01'`, `Key1 = '10061'`, which has two lines: Line 1 with `RevisionNum = 'B'`, `ExtWeight = 45.5000` and Line 2 with `RevisionNum = 'A'`, `ExtWeight = 120.0000` in [`sql/01-erp-app-schema.sql`](../../sql/01-erp-app-schema.sql)):
   ```sql
   USE [ErpReporting];
   DECLARE @Guid NVARCHAR(36) = N'b2222222222222222222222222222202';
   EXEC dbo.usp_StageEpicorReport
       @ReportType = N'OrderAck',
       @Company    = N'MFG01',
       @Key1       = N'10061',
       @TableGuid  = @Guid OUTPUT;
   SELECT @Guid AS StagedTableGuid;
   ```
   Because `RevisionNum` and `ExtWeight` were un-excluded in Step 1 before staging, `dbo.[OrderDtl_b2222222222222222222222222222202]` now contains both columns (`[S14]`, Approved Default 20).

### Step 4: Manually Update the `OrderAck` RDL Dataset Query and `<Fields>`
1. Start from the base [`rdl/OrderAck.rdl`](../../rdl/OrderAck.rdl) and open a working copy in **Report Builder** (`[S2]`, §7.4).
2. Open **Dataset Properties** for the **`OrderAck`** dataset (`[S24, S25]`, §8.5) and open the query expression (`fx` — *Default chosen for the lab, not confirmed against Epicor*).
3. In the `SELECT` list (`[S13, S14, S19]`, Explicit Answer 1), add **`T2.RevisionNum`** and **`T2.ExtWeight`** from `dbo.[OrderDtl_" + Parameters!TableGuid.Value + "] T2`, plus **`T5.LblRevisionNum`** and **`T5.LblExtWeight`** from `dbo.[RptLabels_" + Parameters!TableGuid.Value + "] T5` (`[S24, S25]`, §8.5; *label column names in `RptLabels_<GUID>`: Default chosen for the lab, not confirmed against Epicor*):
   ```vb
   + "T2.OrderLine, T2.PartNum, T2.RevisionNum, T2.LineDesc, T2.OrderQty, T2.SalesUM, T2.UnitPrice, T2.ExtWeight, "
   ```
   and in the `T5` label list:
   ```vb
   + "T5.LblPartNum, T5.LblRevisionNum, T5.LblLineDesc, T5.LblOrderQty, T5.LblUnitPrice, T5.LblExtWeight "
   ```
4. Click **OK** on the Query screen, switch to the **Fields** list in **Dataset Properties** (`[S24, S25]`, §8.5), and add (`Add > Query Field` — *Default chosen for the lab, not confirmed against Epicor*):
   - **Field Name**: `RevisionNum` | **Field Source**: `RevisionNum` (`System.String`)
   - **Field Name**: `ExtWeight` | **Field Source**: `ExtWeight` (`System.Decimal`)
   - **Field Name**: `LblRevisionNum` | **Field Source**: `LblRevisionNum` (`System.String`)
   - **Field Name**: `LblExtWeight` | **Field Source**: `LblExtWeight` (`System.String`)
5. Click **OK** on Dataset Properties (`[S24, S25]`, §8.5).

### Step 5: Place `RevisionNum` and `ExtWeight` on the Tablix and Preview
1. In `OrderLinesTablix`:
   - Insert a column to the right of `PartNum` for **Revision**: header `=First(Fields!LblRevisionNum.Value, "OrderAck")`, detail cell `=Fields!RevisionNum.Value`.
   - Insert a column to the right of `UnitPrice` for **Extended Weight**: header `=First(Fields!LblExtWeight.Value, "OrderAck")`, detail cell `=Fields!ExtWeight.Value` formatted as `N2`.
2. Preview the report in Report Builder with `TableGuid = b2222222222222222222222222222202` (`[S21]`, §5.4) and verify that Line 1 displays Rev `B` / Ext Weight `45.50` and Line 2 displays Rev `A` / Ext Weight `120.00`.
3. Save the RDL file (`[S2]`, §7.4).

### Step 6: Upload, Re-Download, and Confirm Round-Trip Integrity
1. In **Report Style**, select your custom `OrderAck` style and upload the RDL via the overflow (three-dot) menu > **Upload SSRS Report** (`[S32, S2]`, §7.7) or in Classic via **Action > Upload SSRS report** (`[S3, S6]`, §7.16).
2. Immediately re-download the report from Report Style via **Download SSRS Report** (`[S32, S8]`, §7.1; Classic **Actions > Download SSRS Report** `[S3]`, §7.14) into a verification folder.
3. **Mandatory Verification (Lab Rule, [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §7c, motivated by `[S1, S8, S9, S11]`)**: Re-download from Report Style and confirm the change (`T2.RevisionNum`, `T2.ExtWeight`, their `<Field>` entries, and the tablix cells) is in the file.
