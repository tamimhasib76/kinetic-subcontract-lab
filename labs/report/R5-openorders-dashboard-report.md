# Lab R5: OpenOrders — Build a Grouped Open Orders BAQ Report with `Calculated_DaysLate`

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-RPT-105` |
| **Client** | MFG01 Manufacturing Corp |
| **Report / Form** | Open Orders Report (`OpenOrders` — BAQ Report Route) |
| **Environment** | Windows Server 2016 / SQL Server 2016 / SSRS 2016 (`[ErpLab]` & `[ErpReporting]`) |
| **Priority** | Medium |
| **Summary** | Customer Service needs a printable **Open Orders** SSRS report built via the **BAQ Report** route (`BAQReportResult_<GUID>` `[C1, S26, S27]`). The report must group all open sales order lines by **Customer** (`Customer_CustID`), show customer subtotals for Open Quantity and Extended Amount, and display **`Calculated_DaysLate`** (computed in the BAQ via `DATEDIFF` `[B11]` against the lab reference date `Erp.LabConstants.FixedLabDate = '2026-10-15'` using the **order header `NeedByDate`**, `OrderHed.NeedByDate`). |

### Acceptance Criteria
1. Understand the **BAQ Report** staging pattern ([`docs/reference/04-cloud-rules.md`](../../docs/reference/04-cloud-rules.md) §2.2 `[C1, S26, S27]`): Epicor executes the BAQ and stages a single flattened table **`dbo.[BAQReportResult_<GUID>]`** (`[S26, S27]`) whose columns use **`<Table>_<Field>`** for database fields and **`Calculated_<FieldName>`** for BAQ calculated fields ([`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) Explicit Answer 3 `[S27]`; [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) §3.4 & Explicit Answer 3 `[B18]`).
2. Verify that `Calculated_DaysLate` uses the **order header `NeedByDate`** (`OrderHed.NeedByDate`) compared against `Erp.LabConstants` (`ConstantName = 'FixedLabDate'`, value `'2026-10-15'`) via `DATEDIFF(day, ...)` (`[B11]`, `02-baq.md` §4.5) rather than `GETDATE()`, so results are deterministic (Approved Default 16).
3. Start from the ungrouped base [`rdl/OpenOrders_Base.rdl`](../../rdl/OpenOrders_Base.rdl):
   - Keep only the single internal `TableGuid` report parameter (`Parameters!TableGuid.Value` `[S13, S14, S19]`) — do not add user-prompted report parameters.
   - Add a **Parent Row Group** on `=Fields!Customer_CustID.Value` with a group header row (`Customer_CustID` and `Customer_Name`) and a group subtotal row (`Sum(Fields!OrderDtl_OrderQty.Value)` and `Sum(Fields!OrderDtl_OrderQty.Value * Fields!OrderDtl_UnitPrice.Value)`).
   - Add a **Days Late** column to the detail row bound to `=Fields!Calculated_DaysLate.Value`.
4. Upload (`[S32, S2, S3, S6]`), re-download from Report Style (`[S32, S8, S3]`), and confirm the change is in the file.

> **Banners & Citations**
> - **BAQ Report Route & `BAQReportResult_<GUID>` Staging**: [`docs/reference/04-cloud-rules.md`](../../docs/reference/04-cloud-rules.md) §2.2 (`[C1, S26, S27]`) and [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) Explicit Answer 3 (`[S26, S27]`).
> - **`<Table>_<Field>` and `Calculated_<FieldName>` Column Naming & `DATEDIFF`**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) §3.4 & Explicit Answer 3 (`[B18]`), [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) Explicit Answer 3 (`[S27]`), and [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) §4.5 (`[B11]`).
> - **Deterministic Aging Reference Date (`FixedLabDate = '2026-10-15'`)**: Approved Default 16 ([`docs/reference/decisions.md`](../../docs/reference/decisions.md)).
> - **Default chosen for the lab, not confirmed against Epicor**: The shared data source (`ErpReportingDS`) is a lab stand-in; BAQ ID `Lab_OpenOrders`, the specific column set in `BAQReportResult_<GUID>`, Report Builder dialog button labels (`fx`), and `RptLabels_<GUID>` label column names are lab defaults.

---

## Step-by-Step Guide

### Step 1: Inspect the Staged `BAQReportResult_<GUID>` Table and `Calculated_DaysLate`
1. In the BAQ Report route (`[C1, S26, S27]`, `04-cloud-rules.md` §2.2), the BAQ joins `Erp.OrderHed`, `Erp.OrderDtl`, and `Erp.Customer` (filtering `OpenOrder = 1`, `VoidOrder = 0`, `OpenLine = 1`, `VoidLine = 0`) and computes `Calculated_DaysLate` in the BAQ via `DATEDIFF` (`[B11]`, `02-baq.md` §4.5) against `Erp.LabConstants` (`ConstantName = 'FixedLabDate'`, `'2026-10-15'`) using the **order header `NeedByDate`** (`OrderHed.NeedByDate`):
   ```sql
   DATEDIFF(day, oh.[NeedByDate], lc.[ConstantDate]) AS [Calculated_DaysLate]
   ```
   Because `Calculated_DaysLate` is computed by the BAQ and staged directly into `dbo.[BAQReportResult_<GUID>]` (`[S26, S27]`), `LabConstants` is not a table in the report RDD (`engines/report/OpenOrders.json`).
2. Stage the `OpenOrders` BAQ Report dataset in `[ErpReporting]` for `Company = 'MFG01'`:
   ```sql
   USE [ErpReporting];
   DECLARE @Guid NVARCHAR(36) = N'd4444444444444444444444444444404';
   EXEC dbo.usp_StageEpicorReport
       @ReportType = N'OpenOrders',
       @Company    = N'MFG01',
       @Key1       = NULL,
       @TableGuid  = @Guid OUTPUT;
   SELECT @Guid AS StagedTableGuid;
   ```
3. Inspect the staged columns on `dbo.[BAQReportResult_d4444444444444444444444444444404]` (`[S27, B18]`):
   - Customer columns: `Customer_CustID`, `Customer_Name`
   - Order header columns: `OrderHed_Company`, `OrderHed_OrderNum`, `OrderHed_PONum`, `OrderHed_OrderDate`, `OrderHed_NeedByDate`, `OrderHed_OrderAmt`
   - Order line columns: `OrderDtl_OrderLine`, `OrderDtl_PartNum`, `OrderDtl_LineDesc`, `OrderDtl_OrderQty`, `OrderDtl_SalesUM`, `OrderDtl_UnitPrice`
   - Calculated column: `Calculated_DaysLate`

### Step 2: Inspect the Base RDL (`rdl/OpenOrders_Base.rdl`)
1. Open a working copy of [`rdl/OpenOrders_Base.rdl`](../../rdl/OpenOrders_Base.rdl) in **Report Builder** (`[S2]`, §7.4).
2. Note that the shared data source `ErpReportingDS` is a lab stand-in (*Default chosen for the lab, not confirmed against Epicor*).
3. Open **Dataset Properties** for the **`BAQReportResult`** dataset (`[S24, S25]`, §8.5) and open the query expression (`fx` — *Default chosen for the lab, not confirmed against Epicor*) to verify that `T1.Calculated_DaysLate` and the `<Table>_<Field>` columns (`[S27, B18]`) are already selected from `dbo.[BAQReportResult_" + Parameters!TableGuid.Value + "] T1 CROSS JOIN dbo.[RptLabels_" + Parameters!TableGuid.Value + "] T2` (`[S19, S26, S27]`):
   ```vb
   ="/* Illustrative base query for lab training — not Epicor proprietary RDL text */ "
   + "SELECT T1.Customer_CustID, T1.Customer_Name, "
   + "T1.OrderHed_Company, T1.OrderHed_OrderNum, T1.OrderHed_PONum, T1.OrderHed_OrderDate, T1.OrderHed_NeedByDate, T1.OrderHed_OrderAmt, "
   + "T1.OrderDtl_OrderLine, T1.OrderDtl_PartNum, T1.OrderDtl_LineDesc, T1.OrderDtl_OrderQty, T1.OrderDtl_SalesUM, T1.OrderDtl_UnitPrice, "
   + "T1.Calculated_DaysLate, "
   + "T2.LblOpenOrdersTitle, T2.LblCustID, T2.LblCustName, T2.LblOrderNum, T2.LblOrderDate, "
   + "T2.LblNeedByDate, T2.LblDaysLate, T2.LblPartNum, T2.LblLineDesc, T2.LblOrderQty, T2.LblUnitPrice "
   + "FROM dbo.[BAQReportResult_" + Parameters!TableGuid.Value + "] T1 "
   + "CROSS JOIN dbo.[RptLabels_" + Parameters!TableGuid.Value + "] T2"
   ```
4. Under the **Parameters** node in Report Builder, confirm that **`TableGuid`** is the **only** parameter on the report (`[S13, S14, S19, S21]`).

### Step 3: Add the `Calculated_DaysLate` Column to the Tablix
1. On the design surface, right-click the **`Need By Date`** (`HdrNeedByDate`) column header in the tablix and select **Insert Column > Right**.
2. Set the header cell expression to `=First(Fields!LblDaysLate.Value, "BAQReportResult")`.
3. Set the detail cell (`RowDaysLate`) expression to:
   ```vb
   =Fields!Calculated_DaysLate.Value
   ```

### Step 4: Group the Tablix by Customer (`Customer_CustID`) with Header and Subtotal Rows
1. In the **Row Groups** pane at the bottom of Report Builder, right-click the **`Details`** group and choose **Add Group > Parent Group**.
2. In the **Tablix group** dialog:
   - **Group by**: `=Fields!Customer_CustID.Value`
   - Check **Add group header** and **Add group footer**.
   - Click **OK**.
3. Format the **Customer Group Header** row across the tablix width with a light grey background (`LightGrey`) and set its expression to:
   ```vb
   ="Customer: " & Fields!Customer_CustID.Value & " - " & Fields!Customer_Name.Value
   ```
4. Format the **Customer Group Footer** (subtotal) row:
   - Label cell: `="Subtotal (" & Fields!Customer_CustID.Value & "):"`
   - Total Open Qty cell (under `OrderDtl_OrderQty`): `=Sum(Fields!OrderDtl_OrderQty.Value)` formatted as `N2`
   - Total Extended Amount cell (under `OrderDtl_UnitPrice`): `=Sum(Fields!OrderDtl_OrderQty.Value * Fields!OrderDtl_UnitPrice.Value)` formatted as `C2`
5. Preview the report in Report Builder with `TableGuid = d4444444444444444444444444444404` (`[S21]`, §5.4) and verify that open orders are grouped by `Customer_CustID`, late orders show positive `Calculated_DaysLate` values (e.g., orders `10061`–`10075` and `10101`–`10115`), future orders show negative values, and customer subtotals calculate accurately.
6. Save the RDL file (`[S2]`, §7.4).

### Step 5: Upload, Re-Download, and Confirm Round-Trip Integrity
1. In **Report Style**, select your custom `OpenOrders` style and upload the RDL via the overflow (three-dot) menu > **Upload SSRS Report** (`[S32, S2]`, §7.7) or in Classic via **Action > Upload SSRS report** (`[S3, S6]`, §7.16).
2. Immediately re-download the report from Report Style via **Download SSRS Report** (`[S32, S8]`, §7.1; Classic **Actions > Download SSRS Report** `[S3]`, §7.14) into a verification folder.
3. **Mandatory Verification (Lab Rule, [`docs/reference/01-ssrs-forms.md`](../../docs/reference/01-ssrs-forms.md) §7c, motivated by `[S1, S8, S9, S11]`)**: Re-download from Report Style and confirm the change (`CustomerGroup` grouping on `=Fields!Customer_CustID.Value`, `=Fields!Calculated_DaysLate.Value`, and the customer subtotal row) is in the file.
