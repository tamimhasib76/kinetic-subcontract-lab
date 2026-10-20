# Lab R4: ARForm — Add Remit-To Block, Ship-To PO (`ShipToPONum_c`), and `InvcDtlShipTo` Relationship

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-RPT-104` |
| **Client** | MFG01 Manufacturing Corp |
| **Report / Form** | Accounts Receivable Invoice (`ARForm`) (`[S17, S18]`) |
| **Environment** | Windows Server 2016 / SQL Server 2016 / SSRS 2016 (`[ErpLab]` & `[ErpReporting]`) |
| **Priority** | High |
| **Summary** | Accounts Receivable requires three additions to the customer invoice (`ARForm`): (1) a boxed **Remit-To** address block (`RemitToName`, `RemitToAddress1`, `RemitToCity`, `RemitToState`, `RemitToZip`), (2) the customer's **Ship-To PO Number** (`ShipToPONum_c`) in the invoice header, and (3) the **`InvcDtlShipTo`** table relationship linking `InvcDtl` to `ShipTo` (`[S17]`) so line-level ship-to addresses can be joined in the RDL. |

### Acceptance Criteria
1. In your custom `ARForm_Custom` RDD (`[S15]`):
   - Un-exclude `RemitToName`, `RemitToAddress1`, `RemitToCity`, `RemitToState`, `RemitToZip`, and `ShipToPONum_c` on `InvcHead` (`[S12, S25]`; in the lab SQL environment, run `dbo.usp_SetRddExclude` for each column).
   - **Add** the **`InvcDtlShipTo`** relationship (`InvcDtl` -> `ShipTo` on `Company = Company`, `ShipToCustNum = CustNum`, `ShipToNum = ShipToNum`, Key = blank/none, Relation Type = `Output`) per [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.12–§3.14 (`[S15, S13, S17]`).
2. Starting from the base [`rdl/ARForm.rdl`](../../rdl/ARForm.rdl), add the Remit-To columns, `ShipToPONum_c`, and `LEFT OUTER JOIN dbo.[ShipTo_" + Parameters!TableGuid.Value + "] T4` (`[S17, S18]`) to the `ARForm` dataset query expression and `<Fields>` collection (without **Sync Dataset** `[S24, S25]`).
3. Add the boxed `RemitToBlock` and `HeaderShipToPO` textboxes to the invoice header canvas.
4. Upload (`[S32, S2, S3, S6]`), re-download from Report Style (`[S32, S8, S3]`), and confirm the change is in the file.

> **Banners & Citations**
> - **Standing Question (e) Per-Client Check ([`docs/reference/decisions.md`](../../docs/reference/decisions.md))**: The exact Epicor table and column names for Remit-To address and Ship-To PO on `ARForm` must be verified **per client** in Epicor (**Field Help > Technical Details** — *Default chosen for the lab, not confirmed against Epicor* — and the client's `ARForm` RDD; also check which RDD the base style actually uses before duplicating, e.g., `ARInvoice` vs `ARForm` `[S18, S35, S36]`, §1.9). In this lab environment, `RemitToName`, `RemitToAddress1`, `RemitToCity`, `RemitToState`, `RemitToZip`, and UD column `ShipToPONum_c` (Approved Default 19: UD columns end with `_c` and contain no other underscores) are placed on `Erp.InvcHead` with `Exclude = 1` in the base RDD.
> - **Adding `ShipTo` to `ARForm` (`InvcDtlShipTo` Relationship)**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.12–§3.14 & Explicit Answer 5 (`[S15, S13, S17, S18]`).
> - **RDD Exclusions & Manual RDL Editing (No Sync Dataset)**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.4–§3.7 (`[S12, S13, S14, S25]`) and §8.1–§8.2 & §8.5 (`[S24, S25]`).
> - **Lab Design (Approved Default 20, [`docs/reference/decisions.md`](../../docs/reference/decisions.md))**: Un-excluding columns via `dbo.usp_SetRddExclude` affects only subsequent `dbo.usp_StageEpicorReport` runs.
> - **Default chosen for the lab, not confirmed against Epicor**: Custom RDD code `ARForm_Custom`, `"Field Help > Technical Details"`, `"Actions > Duplicate Report"`, `"New > New Table"` / `"New > New Relationship"` / `"New > New Relationship Field"` UI labels (§3.15), Copy Report Style dialog field values (such as style number `1001`), the lab `Report Location` path `reports/CustomReports/ARInvoice/ARForm_Custom`, label columns `LblRemitTo` and `LblShipToPO`, Report Builder dialog button labels (`fx`, `Add > Query Field`), shared data source `ErpReportingDS`, and the SQL stand-in procedure `dbo.usp_SetRddExclude`.

---

## Step-by-Step Guide

### Step 1: Duplicate `ARForm` RDD, Un-exclude `InvcHead` Columns, and Add the `InvcDtlShipTo` Relationship
1. Perform the **Standing Question (e) per-client check**: In a live client environment, check which RDD the base style actually uses before duplicating (`ARInvoice` vs `ARForm` `[S18, S35, S36]`, §1.9) and inspect **Field Help > Technical Details** (*Default chosen for the lab, not confirmed against Epicor*) and the client's RDD to verify which table and column store the client's Remit-To block and Ship-To PO. In this lab, they reside on `Erp.InvcHead` (`RemitToName`, `RemitToAddress1`, `RemitToCity`, `RemitToState`, `RemitToZip`, and UD column `ShipToPONum_c`).
2. Open **Report Data Definition**, load **`ARForm`**, and duplicate the RDD (`[S15]`, §3.1) via **Actions > Duplicate Report** (*Default chosen for the lab, not confirmed against Epicor*) to create **`ARForm_Custom`** (*Default chosen for the lab, not confirmed against Epicor*).
3. Select **`InvcHead`**, open the **Exclusions** tab (`[S12]`, §3.4), and clear the **Exclude** checkbox (`[S12, S25]`, §3.5) for `RemitToName`, `RemitToAddress1`, `RemitToCity`, `RemitToState`, `RemitToZip`, and `ShipToPONum_c`. The staging table's columns are set by the exclusions in the RDD (`[S14]`, §3.6).
4. **Add the `InvcDtlShipTo` Relationship (`[S15, S13, S17]`, §3.12–§3.14)**:
   - Add table **`ShipTo`** to the RDD if not already present (`[S15, S17]`, §3.12, §3.14; `New > New Table` — *Default chosen for the lab, not confirmed against Epicor*) and refresh before checking its **Exclusions** tab (`[S12]`, §3.4).
   - Create a new relationship (`New > New Relationship` — *Default chosen for the lab, not confirmed against Epicor*, §3.15) with the exact parameters from [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.14 (`[S17]`):
     - **Relationship Name**: `InvcDtlShipTo`
     - **Parent Table**: `InvcDtl`
     - **Child Table**: `ShipTo`
     - **Key**: leave blank / none (`[S15, S17]`, §3.12, §3.14)
     - **Relation Type**: `Output` (`[S15, S17]`, §3.12, §3.14)
   - Add the three relationship fields (`[S13, S17]`, §3.13–§3.14; `New > New Relationship Field` — *Default chosen for the lab, not confirmed against Epicor*):
     1. `ShipToNum` -> `ShipToNum`
     2. `ShipToCustNum` -> `CustNum`
     3. `Company` -> `Company`
   - Ensure the join fields are un-excluded (`[S13, S15, S17]`, §3.7, §3.12, §3.14): `ShipToCustNum` and `ShipToNum` on `InvcDtl`, and `Company`, `CustNum`, and `ShipToNum` on `ShipTo`.
   - Save the RDD.
5. **Lab SQL Stand-In** (*Default chosen for the lab, not confirmed against Epicor*): In SSMS against `[ErpReporting]`, un-exclude the six `InvcHead` columns and record the `InvcDtlShipTo` relationship:
   ```sql
   USE [ErpReporting];

   EXEC dbo.usp_SetRddExclude @RddId = N'ARForm', @TableName = N'InvcHead', @ColumnName = N'RemitToName',     @Exclude = 0;
   EXEC dbo.usp_SetRddExclude @RddId = N'ARForm', @TableName = N'InvcHead', @ColumnName = N'RemitToAddress1', @Exclude = 0;
   EXEC dbo.usp_SetRddExclude @RddId = N'ARForm', @TableName = N'InvcHead', @ColumnName = N'RemitToCity',     @Exclude = 0;
   EXEC dbo.usp_SetRddExclude @RddId = N'ARForm', @TableName = N'InvcHead', @ColumnName = N'RemitToState',    @Exclude = 0;
   EXEC dbo.usp_SetRddExclude @RddId = N'ARForm', @TableName = N'InvcHead', @ColumnName = N'RemitToZip',      @Exclude = 0;
   EXEC dbo.usp_SetRddExclude @RddId = N'ARForm', @TableName = N'InvcHead', @ColumnName = N'ShipToPONum_c',   @Exclude = 0;

   IF NOT EXISTS (SELECT 1 FROM dbo.RddRelationship WHERE RddId = N'ARForm' AND RelationshipName = N'InvcDtlShipTo')
   BEGIN
       INSERT INTO dbo.RddRelationship (RddId, RelationshipName, ParentTable, ChildTable, RelationType, RelationshipKeys)
       VALUES (N'ARForm', N'InvcDtlShipTo', N'InvcDtl', N'ShipTo', N'Output', N'Company=Company, ShipToCustNum=CustNum, ShipToNum=ShipToNum');
   END;
   ```

### Step 2: Copy the `ARForm` Report Style and Stage Test Data (`InvoiceNum = 90001`)
1. Open **Report Style**, load **`ARForm`**, select **`Standard - SSRS`**, and copy the style via **Copy Report Style** (`[S1, S5, S9]`, §1.1–§1.4).
2. Assign **`ARForm_Custom`** in the **Data Definition** field (`[S15]`, §1.8) and set **Report Location** under `reports/CustomReports/...` (`[S3, S5]`, §2.1–§2.3; match the client's existing style on whether `.rdl` is included `[S5, S32]`; for this lab we use `reports/CustomReports/ARInvoice/ARForm_Custom` — *Default chosen for the lab, not confirmed against Epicor*).
3. When running the report in Epicor to stage test data, set **Archive Period** = **Day** and copy the GUID from the System Monitor **Reports** tab (`[S21]`, §5.4). In the lab SQL environment, stage test data in `[ErpReporting]` for `Company = 'MFG01'`, `InvoiceNum = '90001'` (where `Erp.InvcHead` has `ShipToPONum_c = 'PO-9912'` and Remit-To `'ErpLab Remittance Processing'` in [`sql/01-erp-app-schema.sql`](../../sql/01-erp-app-schema.sql)):
   ```sql
   USE [ErpReporting];
   DECLARE @Guid NVARCHAR(36) = N'c3333333333333333333333333333303';
   EXEC dbo.usp_StageEpicorReport
       @ReportType = N'ARForm',
       @Company    = N'MFG01',
       @Key1       = N'90001',
       @TableGuid  = @Guid OUTPUT;
   SELECT @Guid AS StagedTableGuid;
   ```

### Step 3: Manually Update the `ARForm` RDL Dataset Query and `<Fields>`
1. Start from the base [`rdl/ARForm.rdl`](../../rdl/ARForm.rdl) and open a working copy in **Report Builder** (`[S2]`, §7.4).
2. Open **Dataset Properties** for the **`ARForm`** dataset (`[S24, S25]`, §8.5) and open the query expression (`fx` — *Default chosen for the lab, not confirmed against Epicor*).
3. Add the Remit-To columns, `T1.ShipToPONum_c`, the `T4` (`ShipTo_<GUID>`) columns, and the `LEFT OUTER JOIN dbo.[ShipTo_" + Parameters!TableGuid.Value + "] T4` clause (`[S17, S18]`, §3.14 & Explicit Answer 5; `[S24, S25]`, §8.5):
   ```vb
   + "SELECT T1.Company, T1.InvoiceNum, T1.InvoiceDate, T1.OrderNum, T1.InvoiceAmt, T1.TermsCode, "
   + "T1.RemitToName, T1.RemitToAddress1, T1.RemitToCity, T1.RemitToState, T1.RemitToZip, T1.ShipToPONum_c, "
   + "T2.InvoiceLine, T2.PackNum, T2.PackLine, T2.PartNum, T2.LineDesc, T2.SellingShipQty, T2.UnitPrice, T2.ExtPrice, "
   + "T3.CustID, T3.Name AS CustName, T3.Address1 AS BillToAddress1, T3.City AS BillToCity, T3.State AS BillToState, T3.Zip AS BillToZip, "
   + "T4.Name AS ShipToName, T4.Address1 AS ShipToAddress1, T4.City AS ShipToCity, T4.State AS ShipToState, T4.Zip AS ShipToZip, "
   + "T5.LblInvoiceTitle, T5.LblInvoiceNum, T5.LblInvoiceDate, T5.LblOrderNum, T5.LblTermsCode, "
   + "T5.LblRemitTo, T5.LblShipToPO, T5.LblPartNum, T5.LblLineDesc, T5.LblShipQty, T5.LblUnitPrice, T5.LblExtPrice "
   + "FROM dbo.[InvcHead_" + Parameters!TableGuid.Value + "] T1 "
   + "INNER JOIN dbo.[InvcDtl_" + Parameters!TableGuid.Value + "] T2 ON T1.Company = T2.Company AND T1.InvoiceNum = T2.InvoiceNum "
   + "LEFT OUTER JOIN dbo.[Customer_" + Parameters!TableGuid.Value + "] T3 ON T1.Company = T3.Company AND T1.CustNum = T3.CustNum "
   + "LEFT OUTER JOIN dbo.[ShipTo_" + Parameters!TableGuid.Value + "] T4 ON T2.Company = T4.Company AND T2.ShipToCustNum = T4.CustNum AND T2.ShipToNum = T4.ShipToNum "
   + "CROSS JOIN dbo.[RptLabels_" + Parameters!TableGuid.Value + "] T5"
   ```
4. Click **OK** on the Query screen, switch to the **Fields** list in **Dataset Properties** (`[S24, S25]`, §8.5), and add (`Add > Query Field` — *Default chosen for the lab, not confirmed against Epicor*):
   - `RemitToName`, `RemitToAddress1`, `RemitToCity`, `RemitToState`, `RemitToZip`, `ShipToPONum_c` (`System.String`)
   - `ShipToName`, `ShipToAddress1`, `ShipToCity`, `ShipToState`, `ShipToZip` (`System.String`)
   - `LblRemitTo`, `LblShipToPO` (`System.String`)
5. Click **OK** on Dataset Properties (`[S24, S25]`, §8.5).

### Step 4: Add the Remit-To Block and Ship-To PO Textboxes to the Header
1. Add a textbox named **`HeaderShipToPO`** below `HeaderInvoiceNum` with the expression:
   ```vb
   =First(Fields!LblShipToPO.Value, "ARForm") & " " & First(Fields!ShipToPONum_c.Value, "ARForm")
   ```
2. Add a boxed textbox named **`RemitToBlock`** in the upper-right header area (`Left: 3.35in`, `Top: 0.1in`, `Width: 3in`, `Height: 0.95in`, `Border: Solid`) with the expression:
   ```vb
   =First(Fields!LblRemitTo.Value, "ARForm") & vbCrLf
   & First(Fields!RemitToName.Value, "ARForm") & vbCrLf
   & First(Fields!RemitToAddress1.Value, "ARForm") & vbCrLf
   & First(Fields!RemitToCity.Value, "ARForm") & ", " & First(Fields!RemitToState.Value, "ARForm") & " " & First(Fields!RemitToZip.Value, "ARForm")
   ```
3. Preview the report in Report Builder with `TableGuid = c3333333333333333333333333333303` (`[S21]`, §5.4; `Company = 'MFG01'`, `InvoiceNum = '90001'`) and verify that **`Ship-To PO #: PO-9912`** and the **`ErpLab Remittance Processing / P.O. Box 75000 / Chicago, IL 60675`** block render cleanly.
4. Save the RDL file (`[S2]`, §7.4).

### Step 5: Upload, Re-Download, and Confirm Round-Trip Integrity
1. In **Report Style**, select your custom `ARForm` style and upload the RDL via the overflow (three-dot) menu > **Upload SSRS Report** (`[S32, S2]`, §7.7) or in Classic via **Action > Upload SSRS report** (`[S3, S6]`, §7.16).
2. Immediately re-download the report from Report Style via **Download SSRS Report** (`[S32, S8]`, §7.1; Classic **Actions > Download SSRS Report** `[S3]`, §7.14) into a verification folder.
3. **Mandatory Verification (Lab Rule, [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §7c, motivated by `[S1, S8, S9, S11]`)**: Re-download from Report Style and confirm the change (`RemitTo*` fields, `ShipToPONum_c`, `ShipTo_<GUID>` join, `RemitToBlock`, and `HeaderShipToPO`) is in the file.
