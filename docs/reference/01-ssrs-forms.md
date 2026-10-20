# 01 — SSRS Forms in Epicor Kinetic: Report Style, RDD, Design, Upload

Scope: ticket type 1 (RDL field modifications on standard SSRS forms).
Research date: 2026-10-20. Research method: WebSearch/WebFetch of public pages only.

## How to read this file

- **CONFIRMED**: a cited source says this. "Forum" means a community post on
  epiusers.help, not Epicor documentation. A CONFIRMED forum claim is only as
  strong as that post. It is **not** proof of how every release behaves.
- **CONFLICTING**: cited sources disagree. Both are cited.
- **UNVERIFIED**: no source found. Do not build lab behavior on it until it is
  confirmed (see `needs-confirmation.md`, written at checkpoint 2).
- The release is noted when a source names one. "No release named" means the
  thread did not say.
- No official Epicor Kinetic help page was reachable for any topic in this file
  (see "Gated / unreachable sources" at the end). Every CONFIRMED item below
  rests on forum posts or Microsoft documentation.

## Sources

| ID | Title | URL | Post date(s) | Release named |
|----|-------|-----|--------------|---------------|
| S1 | SSRS Generate For Design Step-by-Step | https://www.epiusers.help/t/ssrs-generate-for-design-step-by-step/134452 | 2026-04-30 | 2025.2 (2025.2.16 for publish issues) |
| S2 | SSRS Report uploading zipped to Cloud (page 1) | https://www.epiusers.help/t/ssrs-report-uploading-zipped-to-cloud/93083 | 2022-08-04 | 2022.1.8; 2021.2 |
| S3 | SSRS Report uploading zipped to Cloud (page 2) | https://www.epiusers.help/t/ssrs-report-uploading-zipped-to-cloud/93083?page=2 | 2022-08-04 to 2022-08-11 | none (one poster says "Classic") |
| S4 | Kinetic Report Style Maintenance and Downloading/Uploading Reports | https://www.epiusers.help/t/kinetic-report-style-maintenance-and-downloading-uploading-reports/118592 | 2024-09-05 to 2024-09-06 | none |
| S5 | Modify SSRS report - Kinetic cloud | https://epiusers.help/t/modify-ssrs-report-kinetic-cloud/123126 | 2025-02-11 | none (cloud) |
| S6 | Kinetic SSRS Upload Error Question | https://epiusers.help/t/kinetic-ssrs-upload-error-question/122911 | 2025-02-04 to 2025-09-18 | 2024.2.7; 2024.2.11 |
| S7 | Kinetic Report Style .RDL Upload Gotcha | https://www.epiusers.help/t/kinetic-report-style-rdl-upload-gotcha/135625 | 2026-06-19 to 2026-06-22 | none |
| S8 | On Cadence Kinetic Cloud and SSRS (page 1) | https://www.epiusers.help/t/on-cadence-kinetic-cloud-and-ssrs/130306 | 2025-10-27 to 2025-10-28 | Pilot 2025.2.4 |
| S9 | On Cadence Kinetic Cloud and SSRS (page 2) | https://www.epiusers.help/t/on-cadence-kinetic-cloud-and-ssrs/130306?page=2 | 2025-10-28 to 2025-11-11 | 2025.1; 2025.2.5 |
| S10 | Kinetic 2024.1 SSRS deployment | https://www.epiusers.help/t/kinetic-2024-1-ssrs-deployment/113820 | 2024-04-18 to 2024-06-27 | 2024.1; 2024.1.5 |
| S11 | SSRS Report Upload not Updating in Epicor | https://www.epiusers.help/t/ssrs-report-upload-not-updating-in-epicor/119149 | 2024-09-23 to 2025-01-23 | 2024.1 (one poster) |
| S12 | Report Data Definition | https://www.epiusers.help/t/report-data-definition/98460 | 2023-01-18 | none (ERP 10 category) |
| S13 | Logic behind Report Relationships | https://www.epiusers.help/t/logic-behind-report-relationships/115742 | 2024-06-13 to 2024-06-19 | 2024.1; 2024.1.5 |
| S14 | RDD's and Added tables | https://www.epiusers.help/t/rdds-and-added-tables/83231 | 2021-10-05 (pre-2022) | none (ERP 10) |
| S15 | How to another table in SSRS report | https://www.epiusers.help/t/how-to-another-table-in-ssrs-report/105757 | 2023-08-04 to 2023-08-07 | none (Kinetic category) |
| S16 | Adding a Linked Table Description Field to SSRS Report | https://www.epiusers.help/t/adding-a-linked-table-description-field-to-ssrs-report/113474 | 2024-04-05 | none (Kinetic category) |
| S17 | AR Invoice SSRS (page 3) | https://www.epiusers.help/t/ar-invoice-ssrs/107481?page=3 | 2023-09-29 to 2025-01-31 | none (Kinetic category) |
| S18 | ARInvoiceForm - invalid column names errors when making an rdl change after duplicating base rdd | https://www.epiusers.help/t/arinvoiceform-invalid-column-names-errors-when-making-an-rdl-change-after-duplicating-base-rdd/119882 | 2024-10-14 to 2024-10-15; 2025-05-20 to 2025-05-21 | 2024.1.12 |
| S19 | SSRS - Select Distinct - Error in dataset | https://www.epiusers.help/t/ssrs-select-distinct-error-in-dataset/109750 | 2023-12-06 | none (Kinetic category) |
| S20 | SSRS RptParameters - Where do they come from? | https://www.epiusers.help/t/ssrs-rptparameters-where-do-they-come-from/132823 | 2026-02-17 | 2024.2 to 2025.2 upgrade |
| S21 | Report Builder unable to view report | https://epiusers.help/t/report-builder-unable-to-view-report/42935 | 2018-02-21 (pre-2022) | 10.2 |
| S22 | SSRS @TableGuid | https://www.epiusers.help/t/ssrs-tableguid/50457 | 2018-12-07 to 2018-12-11 (pre-2022) | 10.2.200.15 |
| S23 | SSRS Report TableGuid disappears soon after generation | https://www.epiusers.help/t/ssrs-report-tableguid-disappears-soon-after-generation/50171 | 2018-11-29 to 2018-11-30 (pre-2022) | none (ERP 10) |
| S24 | Report Data Definition and Microsoft Report Builder syncing issue? | https://www.epiusers.help/t/report-data-definition-and-microsoft-report-builder-syncing-issue/132042 | 2026-01-16 to 2026-01-30 | 10.2.600.12 |
| S25 | The truth about Report Style "Synch Dataset" | https://www.epiusers.help/t/the-truth-about-report-style-synch-dataset/40000 | 2017-08-23 to 2017-08-25 (pre-2022) | none (ERP 10) |
| S26 | BAQ - SSRS Report - Added Fields | https://www.epiusers.help/t/baq-ssrs-report-added-fields/104290 | 2023-06-21 to 2023-06-22 | none (ERP 10 category) |
| S27 | Adding new field from BAQ to SSRS | https://epiusers.help/t/adding-new-field-from-baq-to-ssrs/107769 | 2023-10-06 to 2023-10-12 | 10.2 (KB reference) |
| S28 | Passing Report Parameters to a BAQ Report | https://epiusers.help/t/passing-report-parameters-to-a-baq-report/71000 | 2020-09-16 to 2020-10-28 (pre-2022) | none (ERP 10) |
| S29 | Access "Advanced BAQ Report" parameters in SSRS RDL template | https://epiusers.help/t/access-advanced-baq-report-parameters-in-ssrs-rdl-template/77340 | 2021-04-06 to 2021-04-07 (pre-2022) | none (E10 cloud) |
| S30 | Microsoft Report Builder 2019 | https://www.epiusers.help/t/microsoft-report-builder-2019/74148 | 2021-01-04 to 2021-02-23 (pre-2022) | 10.2.200.6 (one poster) |
| S31 | Find the Report Definition Schema Version (SSRS) — Microsoft Learn | https://learn.microsoft.com/en-us/sql/reporting-services/reports/find-the-report-definition-schema-version-ssrs?view=sql-server-ver16 | ms.date 2024-09-25 | n/a (Microsoft doc) |
| S32 | SSRS - Creating a SubReport from a new Report Data Definition, Step-by-Step | https://www.epiusers.help/t/ssrs-creating-a-subreport-from-a-new-report-data-definition-step-by-step/134855 | 2026-05-20 to 2026-05-21 | none (cloud) |
| S33 | Add to Order Acknowledgment Query | https://www.epiusers.help/t/add-to-order-acknowledgment-query/49064 | 2018-10-24 (pre-2022) | 10.2.300.0 |
| S34 | Uploaded SSRS Report Applied to all Custom Report Styles | https://epiusers.help/t/uploaded-ssrs-report-applied-to-all-custom-report-styles/102783 | 2023-05-15 | 2022.2.11 Cloud |

---

## 1. Report Style copy

| # | What the developer does | Screen / menu / field | Exact value | Label | Source |
|---|-------------------------|-----------------------|-------------|-------|--------|
| 1.1 | Open the report's style list and copy the system style before changing anything. | Report Style app → overflow menu → **Copy Report Style** | — | CONFIRMED (forum) | S1 |
| 1.2 | You cannot design a system style directly. On a system style, **Generate for Design** is greyed out. | Print slideout overflow → **Generate for Design** (disabled) | Example system style: "Standard - SSRS" | CONFIRMED (forum) | S1 |
| 1.3 | One cloud user's copy path: Report Style → POForm → Style List → Copy Report Style, then download. | Report Style → (Report ID) → **Style List** → **Copy Report Style** | Report ID `POForm` | CONFIRMED (forum) | S5 |
| 1.4 | Cloud support guidance: start from a copy of the out-of-box style, and keep the report names that come in the downloaded zip. Custom report names such as `JobTravCoV2` are "no longer" allowed. | — | — | CONFIRMED (forum, relaying Epicor support, 2025-11-07) | S9 |
| 1.5 | Classic Report Style copy no longer works on new 2024.1 installs (one poster, citing support). | Classic Report Style Maintenance | — | CONFIRMED (forum, single poster) | S10 |
| 1.6 | Copying the standard Pack Slip **RDD** to a new name failed in a 2025.2.4 Pilot; a ticket was open. | Report Data Definition → copy | — | CONFIRMED (forum, single report) | S8 |
| 1.7 | Fields and default values in the Copy Report Style dialog (new style number, description). | — | — | UNVERIFIED | — |
| 1.8 | Assign the copied (duplicated) RDD to the copied style. | Report Style → style detail → data definition field | — | CONFIRMED (forum) | S15 |
| 1.9 | Check which RDD the base style actually uses before duplicating it. In 2024.1.12 the base AR invoice style used the `ARInvoice` RDD, not `ARForm`. | Report Style Maintenance → style → data definition | `ARInvoice` | CONFIRMED (forum) | S18 |

## 2. Report Location

| # | Claim | Exact value | Label | Source |
|---|-------|-------------|-------|--------|
| 2.1 | A custom style's Report Location follows the pattern `reports/CustomReports/<name>`. | `reports/CustomReports/xxx` (Classic example) | CONFIRMED (forum, 2022, Classic) | S3 |
| 2.2 | The downloaded cloud zip holds the folder path `reports\CustomReports\PurchaseOrderForm`. The edited file was `OF_POForm.rdl`. | `reports\CustomReports\PurchaseOrderForm\OF_POForm.rdl` | CONFIRMED (forum) | S5 |
| 2.3 | The RDL name in the Report Location field must match the uploaded file name. A mismatch (`POForm.rdl` vs `OF_POForm.rdl`) made the upload fail. | — | CONFIRMED (forum) | S5 |
| 2.4 | The Report Location is the publish path. Two styles with the same path and file name overwrite each other: both previewed the last upload. Fix: give each style its own path. | — | CONFIRMED (forum, 2022.2.11 Cloud) | S34 |
| 2.5 | When re-uploads would not replace an old RDL, the fix was to rename the `.rdl` and update the Report Location to the new name. | — | CONFIRMED (forum) | S11 |
| 2.6 | A failing upload was fixed by creating a new style with a changed folder name in the "Custom Reports" popup. | `SalesOrderAcknowledgment` → `SalesOrderAcknowledgment2` | CONFIRMED (forum, relaying support, 2025.2.5) | S9 |
| 2.7 | From 2024.1, base reports live in the IceCommon database, which is read-only. Custom reports created or imported with Epicor tools are stored in `Ice.CustomReportStore` in the main Kinetic database. Untouched older custom reports still fall back to SSRS. Version history is in `Ice.CustomReportStoreHistory`. | `Ice.CustomReportStore`, `Ice.CustomReportStoreHistory` | CONFIRMED (forum; explanation posted by a poster on the Epicor side, 2024-05-22) | S10 |
| 2.8 | A doubled `CustomReports` segment in the Report Location broke an upload. The fix was to correct the path at Report Style → Style Detail → Detail. | — | CONFIRMED (forum) | S27 |
| 2.9 | Upload is rejected with a message that the path must be inside `reports/CustomReports`. A search snippet showed this, but the post could not be located on fetch. | — | UNVERIFIED | — |
| 2.10 | Exact label of the field in the Kinetic UI ("Report Location" vs other). | — | UNVERIFIED (forum posts use "Report Location"/"report location"; no Kinetic screenshot text available) | S5, S27 |

## 3. RDD Maintenance (Report Data Definition)

### 3a. Duplicate first

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 3.1 | Duplicate the RDD and edit the copy, not the base. One poster suggests suffixing custom copies with `_c`. | CONFIRMED (forum) | S15 |
| 3.2 | Calculated fields in standard RDDs are hard-coded. You can only view them with the SDK. | CONFIRMED (forum) | S15 |
| 3.3 | Some joins are applied in code and do not appear as RDD relationships. Test with a report run before adding a join between tables that already exist; a hidden join can duplicate rows. | CONFIRMED (forum) | S13, S15 |

### 3b. Exclude / include columns

| # | What the developer does | Screen / field | Label | Source |
|---|-------------------------|----------------|-------|--------|
| 3.4 | After adding a table, refresh first; otherwise the Exclusions tab stays empty. | Report Data Definition → table → **Exclusions** tab | CONFIRMED (forum, 2023) | S12 |
| 3.5 | To include a field, clear its **Exclude** checkbox on the correct table's Exclusions tab. | Exclusions tab → Exclude checkbox | CONFIRMED (forum) | S12, S25 |
| 3.6 | The temp (staging) table's columns are set by the exclusions in the RDD. | — | CONFIRMED (forum, 2021, ERP 10) | S14 |
| 3.7 | Any field that is shown on the report, used in an expression, or used as a join key must stay included. | — | CONFIRMED (forum) | S13 |

### 3c. Linked tables

| # | What the developer does | Screen / path | Label | Source |
|---|-------------------------|---------------|-------|--------|
| 3.8 | Select the report table in the tree. Open **Data Sources\Report Table\Linked Tables\Pick Links**. Move the key (example: `PartNum`) to **Picked**. | Report Data Definition tree | CONFIRMED (forum, 2023) | S12 |
| 3.9 | Open the **Description Fields** tab. Move the wanted field from **Available** to **Picked**. | Description Fields tab | CONFIRMED (forum) | S12 |
| 3.10 | Linked tables are a shortcut that avoids a new table and relationship. Kinetic can make the "Like"-field link for you. | — | CONFIRMED (forum) | S12, S13 |
| 3.11 | On Kinetic Cloud (2024.1.5), the Linked Tables and Dataset Relationships modules showed blank. Dataset Relationships worked in the Classic client but not in Kinetic. | — | CONFIRMED (forum, two posters) | S13 |

### 3d. Relationships

| # | What the developer does | Field / value | Label | Source |
|---|-------------------------|---------------|-------|--------|
| 3.12 | Add the table to the RDD and join it to an existing table. Enter the Parent table, then the Child table, leave **Key** blank, and set **Relation Type** to **Output**. Mark the join fields as included. | Relation Type = `Output` | CONFIRMED (forum) | S15 |
| 3.13 | At a minimum, a relationship needs Parent Table, Parent Field, Child Table and Child Field. | — | CONFIRMED (forum) | S13 |
| 3.14 | Example relationship from an AR invoice fix: name `InvcDtlShipTo`; parent `InvcDtl`; child `ShipTo`; Key none; RelationType `Output`; fields `ShipToNum`→`ShipToNum`, `ShipToCustNum`→`CustNum`, `Company`→`Company`. Also un-exclude `ShipToCustNum` and `ShipToNum` on InvcDtl, and `Company`, `CustNum` and `ShipToNum` on ShipTo. | — | CONFIRMED (forum) | S17 |
| 3.15 | A "Defined" (Definition) relationship acts like an inner join and can reduce the data the original RDD would have produced. | — | CONFIRMED (forum, 2021, ERP 10; Kinetic behavior UNVERIFIED) | S14 |
| 3.16 | A table added with no relationship is generated empty. A basic relation such as `Company=Company` is needed to get the whole table. | — | CONFIRMED (forum, 2021, ERP 10) | S14 |
| 3.17 | You cannot link the same table twice in one RDD. | — | CONFIRMED (forum, single poster) | S13 |
| 3.18 | Full list of Relation Type values and their exact join semantics in Kinetic 2022+. | — | UNVERIFIED | — |
| 3.19 | There is a column-count limit (a figure near 1,048 appeared in a search snippet). | — | UNVERIFIED (not located on fetch) | — |

## 4. Generate for Design

Prerequisites (CONFIRMED, forum, 2025.2, S1):
- MS Report Builder installed and set as the default app for `.rdl` files.
- Epicor Edge Agent installed and configured.
- **SSRS Report Designer** rights enabled for the user on the **System Access** card.

| # | Step | Exact UI name | Label | Source |
|---|------|---------------|-------|--------|
| 4.1 | On the report's print screen, open the overflow menu of the **Print** slideout and choose **Generate for Design**. | Print slideout → overflow → `Generate for Design` | CONFIRMED (forum, 2025.2) | S1 |
| 4.2 | Generate for Design is greyed out on system styles; copy the style first. | — | CONFIRMED (forum) | S1 |
| 4.3 | Generate for Design is available to cloud customers. | — | CONFIRMED (forum, 2022) | S3 |
| 4.4 | Whether Generate for Design works for every custom report or only BAQ reports. | — | CONFLICTING: works "for ANY custom report including SSRS reports" (2021.2 poster) vs "only BAQ reports" (another poster, not confirmed) | S2 |

## 5. System Monitor

| # | Step / claim | Exact UI name / value | Label | Source |
|---|--------------|-----------------------|-------|--------|
| 5.1 | Open **Notifications → System Monitor** and go to the **Reports** tab. Select the report's row. | — | CONFIRMED (forum, 2025.2) | S1 |
| 5.2 | Confirm **Design Mode** = `Available`. | Design Mode column | CONFIRMED (forum) | S1 |
| 5.3 | From the Reports overflow menu, choose **Design SSRS Report**. It is greyed out unless the row shows Design Mode `Available`. | `Design SSRS Report` | CONFIRMED (forum) | S1 |
| 5.4 | Classic/E10 method: run the report with **Archive Period** = Day, copy the GUID from the System Monitor Reports tab, and paste it into the TableGuid parameter in Report Builder. | Archive Period = `Day` | CONFIRMED (forum, 2018, 10.2; pre-Kinetic) | S21 |
| 5.5 | With Archive Period = 0 days, the GUID tables stayed about 1 minute and then disappeared, giving "invalid object name". | — | CONFIRMED (forum, 2018, ERP 10) | S23 |
| 5.6 | You can read the GUID from `Ice.SysRptLst` (from the FileName). | `Ice.SysRptLst.FileName` | CONFIRMED (forum, 2018, 10.2.200.15) | S22 |
| 5.7 | A reprint from System Monitor skips data generation, if the archive period allows it. | — | CONFIRMED (forum, single poster, 2026) | S20 |

## 6. SSRS Report Design (Download / Design / Preview / Publish)

| # | Step | Status / exact value | Label | Source |
|---|------|----------------------|-------|--------|
| 6.1 | A new browser tab **SSRS Report Design** opens. Confirm Status = `Available` and User is blank. | Status `Available` | CONFIRMED (forum, 2025.2) | S1 |
| 6.2 | Overflow → **Download**. Status changes to `Active` and User shows your username. Nothing lands in a normal download folder; the Edge Agent stores the files locally. | Status `Active` | CONFIRMED (forum) | S1 |
| 6.3 | Overflow → **Design**. Report Builder shows **Connect to Report Server**; press **Cancel**. The report opens for editing. | — | CONFIRMED (forum) | S1 |
| 6.4 | Edit, then **Save** in Report Builder. Saving only makes the edit available to the server for Preview/Publish. It does not change the style permanently. | — | CONFIRMED (forum) | S1 |
| 6.5 | Overflow → **Preview** to view output. Repeat edit/save/preview as needed. | — | CONFIRMED (forum) | S1, S9 |
| 6.6 | Overflow → **Cancel** discards all changes; Status returns to `Available`. | — | CONFIRMED (forum) | S1 |
| 6.7 | Overflow → **Publish**, then Yes/No confirmation, saves permanently; Status returns to `Available`. | — | CONFIRMED (forum) | S1 |
| 6.8 | Back up the changed report in **Solution Workbench**. | — | CONFIRMED (forum) | S1 |
| 6.9 | Does Publish reliably save the changed RDL? | — | CONFLICTING: on 2025.2.16 one poster found Publish did not upload the RDL (case CS0005452645); another found it worked after a page reload; a third saw "success" but no change (S1). On 2025.1, Publish returned ERROR while a zip upload through Report Style succeeded (S9). Another poster said the Kinetic design path "doesn't work currently" (S9). | S1, S9 |
| 6.10 | The download location cannot be controlled, and Edge Agent setup is required for download. | — | CONFIRMED (forum) | S11 |

## 7. Cloud zip upload (answers question 7)

### 7a. Kinetic Report Style path

| # | Step | Exact value | Label | Source |
|---|------|-------------|-------|--------|
| 7.1 | In the copied style, overflow (three-dot) menu → **Download SSRS Report**. You get a zip. | — | CONFIRMED (forum) | S32, S8 |
| 7.2 | Extract the zip. You cannot edit files directly inside the zip. | — | CONFIRMED (forum) | S4, S2 |
| 7.3 | Keep the folder path that matches the Report Location. | — | CONFIRMED (forum) | S32, S5 |
| 7.4 | Edit the `.rdl` in Report Builder and save. A zip may contain sub-reports, so it is not always just one RDL. | — | CONFIRMED (forum) | S2 |
| 7.5 | Re-zip with the same folder structure. One working structure was `FOLDERNAME\reports\CustomReports\PurchaseOrderForm\POForm.rdl`. | — | CONFIRMED (forum) | S5 |
| 7.6 | Name the zip `reports.zip` with a lowercase `r`. Otherwise the upload fails with **"Archive with reports was not found"**. The top folder inside may be `Reports` (capital R). | `reports.zip` | CONFIRMED (forum, verified by a second poster) | S7, S5 |
| 7.7 | Upload from the style: three-dot menu → **Upload SSRS Report**. The prompt reads "select zip file with reports". The success message should list each file name. | — | CONFIRMED (forum) | S32, S2 |
| 7.8 | Verify with three-dot menu → **Generate Form**. | — | CONFIRMED (forum) | S32 |
| 7.9 | The Kinetic Report Style screen does not show SSRS errors. Use **Classic** Report Style to see them. | — | CONFIRMED (forum, several posters) | S5, S6 |
| 7.10 | Kinetic upload error text: "Undefined", Program `Ice.BO.ReportSvc`, Method `ExtractAndUploadReports.zip`. Posters link it to a problem inside the RDL; a path problem gives "Could not find a part of the path" instead. | — | CONFIRMED (forum) | S6 |
| 7.11 | Does the upload work from the browser, or only from the client? | — | CONFLICTING: "does not work in the browser, only the client" (S5, jkane) vs cloud zip upload working (S5, Gillian; S8, Brendan). Edge Agent is needed in the browser (S11). | S5, S8, S11 |
| 7.12 | Does a zip upload reliably replace the RDL on cloud 2025.2? | — | CONFLICTING: "works perfectly" (S8, Brendan) vs no change and no errors on Pilot 2025.2.4 (S8, Garret) | S8 |
| 7.13 | For sub-reports, open an EpicCare ticket. Avoid special characters in sub-report names (`CoPartDataSub`, not `CoPartData-Sub`). | — | CONFIRMED (forum, relaying support) | S9 |

### 7b. Classic Report Style path (no zipping)

| # | Step | Label | Source |
|---|------|-------|--------|
| 7.14 | Report Style Maintenance → select Report ID and style → **Actions > Download SSRS Report** → choose a local folder. Files keep the Report Location path. | CONFIRMED (forum, 2022, Classic) | S3 |
| 7.15 | Edit the RDL and save it in the same folder. Keep only the target report under `CustomReports`. | CONFIRMED (forum, 2022) | S3 |
| 7.16 | **Action > Upload SSRS report**. Select the top-level folder; do not drill down. | CONFIRMED (forum) | S3, S6 |
| 7.17 | The Classic screen zips behind the scenes. | CONFIRMED (forum) | S2 |

### 7c. Folder rules summary

- Path must match the style's Report Location, and the file name must match. CONFIRMED (S5, S27).
- One path per style when the RDLs differ. CONFIRMED (S34).
- Zip file name `reports.zip`, lowercase. CONFIRMED (S7).
- Hard rule that the path must start `reports/CustomReports`. UNVERIFIED (2.9).

## 8. Sync Dataset risks

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 8.1 | Do not use Sync Dataset (Synch Dataset) on standard Epicor reports. One poster: it will "pollute" the report "to where you will not be able to run it". | CONFIRMED (forum, 2026, three posters agree) | S24 |
| 8.2 | Effects seen: dataset structure changes, field names change, dataset queries break. A reserved-word field name (`Primary`, `Percent`) caused "Incorrect syntax near the keyword". | CONFIRMED (forum, 2017, ERP 10) | S25 |
| 8.3 | Sync Dataset works acceptably for simple BAQ reports you built yourself, but had problems with Union sub-queries. | CONFIRMED (forum) | S24, S25 |
| 8.4 | Report Style **Actions → Synchronize the Dataset** exists for BAQ reports. Back up the RDL first; it has been buggy. | CONFIRMED (forum, 2023) | S26 |
| 8.5 | Safe alternative: un-exclude the field in the RDD, then add it to the dataset query SELECT and to the dataset **Fields** list in Report Builder. Click OK on both the Query and Dataset Properties screens. Remove textboxes that reference removed fields. | CONFIRMED (forum) | S24, S25 |

---

## Explicit answers

### (1) RptLabels_<GUID> and RptParameter_<GUID> column structure

- At run time each RDD table is written to the reports database as `<TableName>_<GUID>`. The RDL query reads them through the `TableGuid` parameter. CONFIRMED (forum) — S14, S13, S19.
- **RptLabels_<GUID>**:
  - Joined on `RptLanguageID`: `LEFT OUTER JOIN RptLabels_" + Parameters!TableGuid.Value + " T3 ON T1.RptLanguageID = T3.RptLanguageID`. CONFIRMED (forum, 2023) — S19.
  - Holds many `RptLiterals*` columns, for example `RptLiteralsLblOf`, `RptLiteralsLblContinueOnNext`, `RptLiteralsLblComeFrom`, `RptLiteralsLblPCID`, `RptLiteralsLCommodityCode`, `RptLiteralsLEORINumber`, `RptLiteralsLblAttributeSet`. CONFIRMED (forum, 2023, PackSlip-based query) — S19.
  - Full column list, data types, and whether the set varies by report: UNVERIFIED.
- **RptParameter_<GUID>**:
  - Holds a `UserCriteria` field. For RDD criteria prompts it contains XML with `<RptCriteriaPrompt>` elements and `PromptID`, `PromptValue`, `PromptName` and `Label`. CONFIRMED (forum, 2021, E10 cloud) — S29.
  - Also holds report-specific option columns, for example `DetailCarbonCost` and `PrintCarbonCostDetails`. After a 2024.2 → 2025.2 upgrade the RDL referenced them but they were missing from the table, giving "Invalid column name". CONFIRMED (forum, 2026) — S20.
  - Where those columns are defined: the RDD did not show them. One poster believes they are excluded in the RDD and/or affected by licensing exclusions. UNVERIFIED (poster's belief) — S20.
  - Common columns such as `Company` or a `ReportID`: UNVERIFIED.

### (2) Linked-table field naming in staging, and un-excluding

- Naming is `<LinkKeyField>_<DescriptionField>`, for example `T1.PartNum_SteelGauge_c` (S16, 2024) and `T2.PartNum_PPAP_c` (S12, 2023). CONFIRMED (forum).
- By that pattern, a link on `OrderNum` that picks `ProjManager_c` would produce `OrderNum_ProjManager_c`. The pattern is CONFIRMED; that this exact column appears is UNVERIFIED.
- Underscores inside UD field names may be misparsed as a link separator. UNVERIFIED (seen only in a search snippet).
- Un-excluding:
  - The staging table's columns come from the RDD exclusions (S14, 2021, ERP 10). Clearing **Exclude** therefore adds that column to the `<Table>_<GUID>` tables generated on later runs. CONFIRMED (forum, ERP 10).
  - That only runs generated after the RDD is saved get the new column follows from tables being created per run (S13), but no post states it. UNVERIFIED.
  - Un-excluding does not add the column to the RDL. You must add it to the dataset query and Fields list yourself. CONFIRMED (forum) — S25, S24.

### (3) BAQ Report staging table names and how filters reach the RDL

- Result table: `BAQReportResult_<GUID>`. Typical dataset query: `="SELECT * FROM dbo.[BAQReportResult_" + Parameters!TableGuid.Value + "]"`. CONFIRMED (forum, 2023) — S26, S27.
- Column names are `<Table>_<Field>` and `Calculated_<Name>`, for example `[Part_PartNum]`, `[Customer_CustID]`, `[Calculated_TodayDate]`, `[UD40_Key5]`. CONFIRMED (forum, 2023) — S27.
- Filters/options, older BAQ report format: values are in `BAQReportParameter_<GUID>` under names such as `FILTER1`, `OPTION2` and `CheckBox3`. CONFIRMED (forum, 2021) — S29.
- One working method cross-joined `BAQReportParameter` into the `BAQReportResult` dataset query to expose an option (`Date01`). CONFIRMED (forum, 2020) — S28.
- A parameter set as an RDD criteria prompt does not reach the BAQ. It must be used inside the BAQ or passed through the report query. CONFIRMED (forum, 2020) — S28.
- RDD-based ("Advanced BAQ") reports: prompts arrive in `RptParameter.UserCriteria` as XML (see answer 1). CONFIRMED (forum, 2021) — S29.
- Whether the `BAQReportParameter_<GUID>` format still applies in Kinetic 2022+: UNVERIFIED.

### (4) RDL schema version shipped with Kinetic; Report Builder 2016

- Microsoft: when an `.rdl` with an older namespace is opened in Report Builder, a backup is created and the report is upgraded to the current namespace. Saving it saves the converted file. The report server does not upgrade the definition. The most recent namespace is 2016 (`.../reporting/2016/01/reportdefinition`). CONFIRMED (Microsoft doc) — S31.
- Report Builder 2016 is version 15.0.900. Report Builder 2019 uses the same schema as 2016, and 2016 opens 2019 files. CONFIRMED (forum, 2021) — S30.
- Most Epicor reports were built with Report Builder 3.0. CONFIRMED (forum, 2021, single poster) — S30.
- The namespace in standard Kinetic 2022+ RDLs: UNVERIFIED. No source states it. Check the `<Report xmlns=...>` line of a downloaded standard RDL, as S31 describes.
- Does Report Builder 2016 open and save a Kinetic RDL without upgrading it?
  - If the file uses an older namespace (2008/2010): **no**. Report Builder upgrades it to 2016 on open. CONFIRMED (Microsoft doc) — S31.
  - If the file is already 2016: no upgrade is implied, but no Epicor source confirms this. UNVERIFIED.
- Will cloud accept a 2016-namespace RDL?
  - In 2021, cloud upload of a re-saved 2016 file failed with "invalid target namespace ... 2016/01/reportdefinition ... cannot be upgraded" (10.2.200.6). CONFIRMED (forum, 2021) — S30.
  - Whether that still applies to Kinetic 2022+ cloud: UNVERIFIED.

### (5) PackSlip, SOAck and ARForm

| Form | RDD name | Tables / relationships seen | Main dataset query seen | Label | Source |
|------|----------|-----------------------------|-------------------------|-------|--------|
| PackSlip | "standard Pack Slip RDD" (exact ID UNVERIFIED) | ShipHead → ShipDtl; RptLabels; Company, OrderHed and Carrier added in a custom version | `FROM ShipHead_" + Parameters!TableGuid.Value + " T1 LEFT OUTER JOIN ShipDtl_" + Parameters!TableGuid.Value + " T2 ON T1.Company = T2.Company AND T1.PackNum = T2.PackNum LEFT OUTER JOIN RptLabels_" + Parameters!TableGuid.Value + " T3 ON T1.RptLanguageID = T3.RptLanguageID` | CONFIRMED (forum, 2023; this is a **customized** query, so whether the base query is identical is UNVERIFIED) | S19, S8 |
| SOAck | "SOAck" as an RDD ID: UNVERIFIED. Sources use OrderAck: "OrderAck report" (S1); custom copy `TSGOrderAck` → `TSGOrderAckC` (S24). Base ID `OrderAck`: UNVERIFIED. | OrderHed aliased `T1`; a dataset named `OrderHed` | Full query text: UNVERIFIED (screenshot only in S33) | partial CONFIRMED (forum) | S1, S24, S33 |
| ARForm | `ARForm`; in 2024.1.12 the base AR invoice style uses `ARInvoice` | InvcHead (T1), InvcDtl (T2) as main line table, ShipTo (T12), plus Customer, InvcMisc, InvcChrg, RptLabels, BankAcct, FSCallDt, FSCallMt, FSContDt, FSAExtData, ShipToCust; relationship example `InvcDtlShipTo` | Dataset named `ARForm`. Seen fragment: `LEFT OUTER JOIN ShipTo_" + Parameters!TableGuid.Value + " T12 ON T2.Company = T12.Company AND T2.ShipToCustNum = T12.CustNum AND T2.ShipToNum = T12.ShipToNum`. Full query UNVERIFIED. | CONFIRMED (forum) for listed items | S17, S18 |

- Copying `ARForm` when the base style uses `ARInvoice` caused "Invalid column name 'Calc_TrackByAttribute'". CONFIRMED (forum, 2024.1.12) — S18.
- Complete relationship lists for all three RDDs: UNVERIFIED.

### (7) Report Style cloud zip upload: exact steps and folder rules

See section 7. Short version, all CONFIRMED from forum posts unless marked:
1. Copy the out-of-box style (S9, S1).
2. Three-dot menu → **Download SSRS Report** (S32).
3. Extract the zip (S4).
4. Edit the RDL; keep the file name and folder path that match Report Location (S5, S32).
5. Re-zip as `reports.zip` (lowercase) (S7).
6. Three-dot menu → **Upload SSRS Report** (S32).
7. Check errors in Classic Report Style (S6).
8. Verify with **Generate Form** (S32).

Reliability on 2025.2 cloud: CONFLICTING (S8).

---

## Gated / unreachable sources (for this file)

- Epicor Kinetic Application Help (in-product help for Report Style, Report Data Definition, SSRS Report Design, System Monitor): not publicly reachable; no URL found.
- EpicWeb / Epicor Customer Portal documentation (Kinetic SSRS / Report Designer technical guides): login required; not attempted.
- EpicCare knowledge base: login required; not attempted. Case CS0005452645 (S1) cannot be read.
- epicor.com BAQ product page returned HTTP 403 to WebFetch.
