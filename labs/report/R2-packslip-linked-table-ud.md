# Lab R2: PackSlip — Add a UD Column (`OrderNum_ProjManager_c`) from a Linked Table

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-RPT-102` |
| **Client** | MFG01 Manufacturing Corp |
| **Report / Form** | Packing Slip (`PackSlip`) |
| **Environment** | Windows Server 2016 / SQL Server 2016 / SSRS 2016 (`[ErpLab]` & `[ErpReporting]`) |
| **Priority** | High |
| **Summary** | Project-driven shipments require the Sales Order's **Project Manager** (`Erp.OrderHed.ProjManager_c`) printed on each Packing Slip line. `OrderHed` is not a separate primary table in the base `PackSlip` dataset join, but `ShipDtl` has a **Linked Table** link (`OrderNum`) to `OrderHed` (`[S12, S13]`). Expose `ProjManager_c` via Linked Tables and display `OrderNum_ProjManager_c` on the custom Packing Slip. |

### Acceptance Criteria
1. In your custom `PackSlip_Custom` RDD (`[S15]`), configure **`ShipDtl` > Linked Tables** (`Pick Links` and `Description Fields`) for the **`OrderNum`** link (`OrderHed`) and move **`ProjManager_c`** from **Available** to **Picked** (`[S12]`; in the lab SQL environment, un-exclude `OrderNum_ProjManager_c` on `ShipDtl` via `dbo.usp_SetRddExclude`).
2. Understand how Epicor stages linked-table columns directly onto the parent staging table (`dbo.[ShipDtl_<GUID>]`) using the `<LinkKeyField>_<DescriptionField>` naming convention (`OrderNum_ProjManager_c` `[S12, S16]`, Approved Default 18).
3. Starting from the base [`rdl/PackSlip.rdl`](../../rdl/PackSlip.rdl) (or continuing from your R1 custom RDL), manually add `T2.OrderNum_ProjManager_c` to the `PackSlip` dataset query expression and `<Fields>` collection (without **Sync Dataset** `[S24, S25]`), and add the column to the tablix.
4. Re-upload (`[S32, S2, S3, S6]`), re-download from Report Style (`[S32, S8, S3]`), and confirm the change is in the file.

> **Banners & Citations**
> - **RDD Linked Tables (`Pick Links` & `Description Fields`) Workflow**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.8–§3.10 (`[S12, S13]`).
> - **`<LinkKeyField>_<DescriptionField>` Staged Column Naming & UD `_c` Examples**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) Explicit Answer 2 (`[S12, S16]`, `T1.PartNum_SteelGauge_c`, `T2.PartNum_PPAP_c`) and Approved Defaults 18 & 19 ([`docs/reference/decisions.md`](../../docs/reference/decisions.md)).
> - **RDD Exclusions & Manual RDL Editing (No Sync Dataset)**: [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §3.6 (`[S14]`) and §8.1–§8.2 & §8.5 (`[S24, S25]`).
> - **Lab Design (Approved Default 20, [`docs/reference/decisions.md`](../../docs/reference/decisions.md))**: Un-excluding `OrderNum_ProjManager_c` via `dbo.usp_SetRddExclude` affects only subsequent `dbo.usp_StageEpicorReport` runs.
> - **Default chosen for the lab, not confirmed against Epicor**: Custom RDD code `PackSlip_Custom`, the link-selector dropdown on `Description Fields` (§3.11), the specific UD column `ProjManager_c` / `OrderNum_ProjManager_c` (Approved Default 18 & 19), label column `LblProjManager`, Report Builder dialog button labels (`fx`, `Add > Query Field`), shared data source `ErpReportingDS`, and the SQL stand-in procedure `dbo.usp_SetRddExclude`.

---

## Step-by-Step Guide

### Step 1: Pick `ProjManager_c` on the `ShipDtl -> OrderNum` Linked Table
1. Open **Report Data Definition** and load your duplicated RDD **`PackSlip_Custom`** (`[S15]`, §3.1; *`PackSlip_Custom` name: Default chosen for the lab, not confirmed against Epicor*).
2. Select **`ShipDtl`** in the tree and open **`Data Sources\Report Table\Linked Tables\Pick Links`** to confirm that **`OrderNum`** is in the **Picked** list (`[S12]`, §3.8).
3. Open the **Description Fields** tab (`[S12]`, §3.9):
   - Select the **`OrderNum`** link (*link-selector control on Description Fields: Default chosen for the lab, not confirmed against Epicor*, §3.11).
   - Move **`ProjManager_c`** from **Available** to **Picked** (`[S12]`, §3.9).
4. Save the RDD.
   - **Lab SQL Stand-In** (*Default chosen for the lab, not confirmed against Epicor*): In SSMS against `[ErpReporting]`, un-exclude `OrderNum_ProjManager_c` on `ShipDtl`:
     ```sql
     USE [ErpReporting];
     EXEC dbo.usp_SetRddExclude
         @RddId      = N'PackSlip',
         @TableName  = N'ShipDtl',
         @ColumnName = N'OrderNum_ProjManager_c',
         @Exclude    = 0;
     ```

### Step 2: Verify the Staged Column Name (`OrderNum_ProjManager_c`)
1. Linked tables are a shortcut that avoids adding a new table and relationship (`[S12, S13]`, §3.10). When a field is picked via **Linked Tables > Description Fields**, Epicor stages the column onto the parent staging table (`dbo.[ShipDtl_<GUID>]`) named **`<LinkKeyField>_<DescriptionField>`** (`[S12, S16]`, Explicit Answer 2).
2. Because the link key on `ShipDtl` is **`OrderNum`** and the picked UD column on `OrderHed` is **`ProjManager_c`**, the staged column on `dbo.[ShipDtl_<GUID>]` (`T2`) is named:
   ```text
   OrderNum_ProjManager_c
   ```
   (See [`engines/report/PackSlip.json`](../../engines/report/PackSlip.json), [`sql/02-erp-rpt-staging.sql`](../../sql/02-erp-rpt-staging.sql), [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) Explicit Answer 2 `[S12, S16]`, and Approved Default 18.)
3. Stage a fresh Packing Slip dataset in `[ErpReporting]` for `Company = 'MFG01'`, `PackNum = '50001'` so `dbo.[ShipDtl_<GUID>]` includes `OrderNum_ProjManager_c` (`[S14]`, Approved Default 20):
   ```sql
   USE [ErpReporting];
   DECLARE @Guid NVARCHAR(36) = N'a1111111111111111111111111111101';
   EXEC dbo.usp_StageEpicorReport
       @ReportType = N'PackSlip',
       @Company    = N'MFG01',
       @Key1       = N'50001',
       @TableGuid  = @Guid OUTPUT;
   ```

### Step 3: Add `T2.OrderNum_ProjManager_c` to the RDL Dataset Expression and `<Fields>`
1. Starting from the base [`rdl/PackSlip.rdl`](../../rdl/PackSlip.rdl) (or continuing from your R1 custom RDL), open your working RDL in **Report Builder** (`[S2]`, §7.4).
2. Open **Dataset Properties** for the **`PackSlip`** dataset (`[S24, S25]`, §8.5) and open the query expression (`fx` — *Default chosen for the lab, not confirmed against Epicor*).
3. No `LEFT OUTER JOIN` needs to be added because `OrderNum_ProjManager_c` is staged directly on `dbo.[ShipDtl_" + Parameters!TableGuid.Value + "] T2` (`[S12, S16]`, Explicit Answer 2). Add **`T2.OrderNum_ProjManager_c`** (and `T5.LblProjManager` — *Default chosen for the lab, not confirmed against Epicor*) to the `SELECT` list (`[S24, S25]`, §8.5):
   ```vb
   + "T2.CustPartNum, T2.OrderNum_ProjManager_c, T2.SellingShippedQty, T2.SalesUM, "
   ```
   and in the `T5` label list:
   ```vb
   + "T5.LblPartNum, T5.LblLineDesc, T5.LblCustPartNum, T5.LblShipQty, T5.LblProjManager "
   ```
4. Click **OK** on the Query screen, switch to the **Fields** list in **Dataset Properties** (`[S24, S25]`, §8.5), and add (`Add > Query Field` — *Default chosen for the lab, not confirmed against Epicor*):
   - **Field Name**: `OrderNum_ProjManager_c` | **Field Source**: `OrderNum_ProjManager_c` (`System.String`)
   - **Field Name**: `LblProjManager` | **Field Source**: `LblProjManager` (`System.String`)
5. Click **OK** on Dataset Properties (`[S24, S25]`, §8.5).

### Step 4: Bind the Field on the Tablix and Preview
1. Insert a column in `PackLinesTablix` to the left of `SellingShippedQty`.
2. Set the header cell expression to `=First(Fields!LblProjManager.Value, "PackSlip")`.
3. Set the detail cell expression to `=Fields!OrderNum_ProjManager_c.Value` (`[S12, S16]`, Explicit Answer 2).
4. Preview the report in Report Builder with `TableGuid = a1111111111111111111111111111101` (`[S21]`, §5.4; `Company = 'MFG01'`, `PackNum = '50001'`) and verify that Project Manager **`Sarah Connor`** renders on the line.
5. Save the RDL file (`[S2]`, §7.4).

### Step 5: Upload, Re-Download, and Confirm Round-Trip Integrity
1. In **Report Style**, select your custom `PackSlip` style and upload the RDL via the overflow (three-dot) menu > **Upload SSRS Report** (`[S32, S2]`, §7.7) or in Classic via **Action > Upload SSRS report** (`[S3, S6]`, §7.16).
2. Immediately re-download the report from Report Style via **Download SSRS Report** (`[S32, S8]`, §7.1; Classic **Actions > Download SSRS Report** `[S3]`, §7.14) into a separate verification folder.
3. **Mandatory Verification (Lab Rule, [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §7c, motivated by `[S1, S8, S9, S11]`)**: Re-download from Report Style and confirm the change (`T2.OrderNum_ProjManager_c`, `<Field Name="OrderNum_ProjManager_c">`, and the tablix binding) is in the file.
