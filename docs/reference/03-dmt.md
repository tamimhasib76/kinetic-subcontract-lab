# 03 — DMT Pre-load Validation: Templates, Add/Update, Load Order, Errors, CLI

Scope: ticket type 3 (DMT pre-load validation).
Research date: 2026-10-20. Research method: WebSearch/WebFetch of public pages only.

## How to read this file

- **CONFIRMED**: a cited source says this. "Forum" means a community post on
  epiusers.help. "Epicor" means an Epicor-owned page. A CONFIRMED forum claim is
  only as strong as that post.
- **CONFLICTING**: cited sources disagree. Both are cited.
- **UNVERIFIED**: no source found.
- The release or DMT version is noted when a source names one.
- The official DMT guides (Quick Start, Troubleshooting, Command Line Interface
  Lab, DMT Templates ZIP) are linked from Epicor's public DMT page but hosted on
  EpicWeb, which requires a login. They were not read. No claim below comes from them.
- **Excluded source:** knowledgelib.io "Epicor DMT ... Bulk Import Constraints"
  (2026-03-02) is an AI-generated summary built from blogs. Its error table and
  load order are **not** used as support for any claim.

## Sources

| ID | Title | URL | Post date(s) | Release / DMT version named |
|----|-------|-----|--------------|-----------------------------|
| D1 | DMT Documentation \| Epicor (Epicor-owned) | https://epicordmthelp.z20.web.core.windows.net/ | no date shown | mentions DMT 4.0.50.1, ERP 10.2.500, "DMT Server Processing 2024.1" |
| D2 | DMT Command Line Help — EpicorDMTScripts GitHub wiki (fork of the repo linked from D1) | https://github-wiki-see.page/m/A9G-Data-Droid/EpicorDMTScripts/wiki/DMT-Command-Line-Help | wiki last modified 2021-09-03 | none |
| D3 | Sales Order Combined DMT - Multi Line order errors on last line for OrderRelNum | https://www.epiusers.help/t/sales-order-combined-dmt-multi-line-order-errors-on-last-line-for-orderrelnum/129231 | 2025-09-12 to 2025-09-15 | none (Kinetic category) |
| D4 | DMT - Sales Order Combined | https://www.epiusers.help/t/dmt-sales-order-combined/129519 | 2025-09-24 | none (Kinetic category) |
| D5 | Sales Order Combined DMT (adding records) | https://www.epiusers.help/t/sales-order-combined-dmt-adding-records/76520 | 2021-03-11 to 2021-03-15; 2024-03-21 | none (ERP 10) |
| D6 | DMT Combined type templates | https://www.epiusers.help/t/dmt-combined-type-templates/53044 | 2019-02-27 to 2019-02-28 (pre-2022) | none (ERP 10) |
| D7 | E10 DMT Error Input array is longer than the number of columns (page 1) | https://www.epiusers.help/t/e10-dmt-error-input-array-is-longer-than-the-number-of-columns/49982 | 2018-11-21 to 2018-11-27 (pre-2022) | DMT 4.0.36 / 10.2; DMT 4.0.34 / 10.1.600 |
| D8 | same thread, page 3 | https://www.epiusers.help/t/e10-dmt-error-input-array-is-longer-than-the-number-of-columns/49982?page=3 | 2018-11-27 to 2018-11-29 (pre-2022) | DMT 4.0.36.0 / 10.1.600; DMT 4.0.37.0 / 10.2.200.7 |
| D9 | DMT help (PartPlant warehouse) | https://www.epiusers.help/t/dmt-help/124425 | 2025-03-28 | none (Kinetic category) |
| D10 | DMT error (CustNumCustID) | https://epiusers.help/t/dmt-error/40053 | 2017-08-25 (pre-2022) | none (ERP 10) |
| D11 | DMT how to update ShipTo table? | https://www.epiusers.help/t/dmt-how-to-update-shipto-table/71497 | 2020-10-02 to 2020-10-05 (pre-2022) | none (ERP 10) |
| D12 | DMTing in cases is failing on every row where I am setting custNumCustID with "Invalid Sold To" | https://epiusers.help/t/dmting-in-cases-is-failing-on-every-row-where-i-am-setting-custnumcustid-with-invalid-sold-to/99896 | 2023-02-25 to 2023-02-26 | none (Kinetic category) |
| D13 | DMT Part Error | https://epiusers.help/t/dmt-part-error/106500 | 2023-08-28 to 2023-09-11 | none (Kinetic category) |
| D14 | DMT help (Part required fields) | https://www.epiusers.help/t/dmt-help/78410 | 2021-05-06 to 2021-05-11 (pre-2022) | none (ERP 10) |
| D15 | DMT Versions - known bugs (page 4) | https://www.epiusers.help/t/dmt-versions-known-bugs/53877?page=4 | 2019-11-04 to 2020-05-05 (pre-2022) | DMT 4.0.38.0; 10.2.300–10.2.500 |
| D16 | DMT_NoUIImport_Error.log | https://www.epiusers.help/t/dmt-nouiimport-error-log/79144 | 2021-06-01 to 2022-06-29 | 10.2.700.15 |
| D17 | How to get DMT logs when tool crashes before completion? | https://www.epiusers.help/t/how-to-get-dmt-logs-when-tool-crashes-before-completion/54038 | 2019-03-27 to 2019-04-01 (pre-2022) | DMT 4.0.39.0 |
| D18 | DMT error You do not have permissions, but i do | https://epiusers.help/t/dmt-error-you-do-not-have-permissions-but-i-do/83515 | 2021-10-13 (pre-2022) | none (Kinetic category) |
| D19 | Upload multiple warehouses to a part through DMT | https://www.epiusers.help/t/upload-multiple-warehouses-to-a-part-through-dmt/37109 | 2017-02-01 to 2017-03-01 (pre-2022) | ERP 9 |
| D20 | DMT New Parts | https://www.epiusers.help/t/dmt-new-parts/39829 | 2017-08-15 (pre-2022) | none (ERP 10) |
| D21 | How to Upload Data using Epicor® DMT — Datix (partner blog) | https://datixinc.com/how-to-upload-data-using-epicor-dmt | no date shown | none |
| D22 | Sales order DMT error (price loads as 0) | https://epiusers.help/t/sales-order-dmt-error/71589 | 2020-10-07 (pre-2022) | none (ERP 10) |
| D23 | Customer/Contact Import in E10 | https://www.epiusers.help/t/customer-contact-import-in-e10/50229 | 2018-11-30 to 2018-12-02 (pre-2022) | 10.1 |
| D24 | How to update default records in ShipTo table | https://www.epiusers.help/t/how-to-update-default-records-in-shipto-table/84404 | 2021-11-09 to 2021-11-11 (pre-2022) | none (ERP 10) |

Note: most DMT threads with exact error text are pre-2022 or name no release.
The 2022+ items are D3, D4, D9, D12 and D13.

---

## 1. Template column naming

| # | Claim | Exact value | Label | Source |
|---|-------|-------------|-------|--------|
| 1.1 | Get headers from the DMT **Template Builder**; it opens with the required columns already selected. You may also type the headings into your own data. | — | CONFIRMED (partner blog) | D21 |
| 1.2 | DMT has a **Required** button that lists required fields. It is "not 100% accurate, especially for the combined imports". | — | CONFIRMED (forum, 2018) | D23 |
| 1.3 | Plain templates use the table's field names as headers, for example `Company`, `PartNum`, `Plant`, `WarehouseCode`, `BinNum`. | — | CONFIRMED (forum, 2017, ERP 9) | D19 |
| 1.4 | Combined templates add child-table columns as `<ChildTable>#<Field>`, for example `OrderDtl#OrderLine`, `OrderDtl#PartNum`, `OrderRel#OrderRelNum`, `OrderRel#FirmRelease`. Parent (OrderHed) columns have no prefix: `Company`, `OrderNum`, `CustomerCustID`. | — | CONFIRMED (forum) that these headers are used. That `#` means "child table / field" is an inference: no source defines it (D6) | D3, D4, D7, D8, D6 |
| 1.5 | Lookup columns let you give a user-facing ID and DMT resolves the internal key: `CustNumCustID` (give CustID; DMT sets CustNum) and `CustomerCustID` on Sales Order Combined. | `CustNumCustID`, `CustomerCustID` | CONFIRMED (forum) | D11, D12, D8 |
| 1.6 | Default BAQ export headers usually do not match DMT headers; copy headers from the template. | — | CONFIRMED (forum, 2017) | D10 |
| 1.7 | Column position can matter: moving the `OrderRel#` columns to the end of the file stopped "Invalid Column name 'OrderRelNum'" errors. | — | CONFIRMED (forum, single poster, 2025) | D3 |
| 1.8 | Booleans: use `true`/`false`, not `1`/`0`. Use codes, not descriptions (`FG`, not `Finished Goods`). Plant/warehouse IDs may be case-sensitive. | — | CONFIRMED (forum, 2021; poster-reported fixes) | D14 |
| 1.9 | Hidden characters (a stray carriage return after a value) cause lookup failures. Clean with Excel CLEAN or check in a text editor. | — | CONFIRMED (forum, 2023) | D12 |

## 2. Add vs Update

| # | Claim | Exact value | Label | Source |
|---|-------|-------------|-------|--------|
| 2.1 | CLI switches: `-Add` "Indicates that records should be added"; `-Update` "...updated"; `-Delete` "...deleted". | `-Add`, `-Update`, `-Delete` | CONFIRMED (GitHub wiki, 2021) | D2 |
| 2.2 | PlayLists can set add, delete or update per import. | — | CONFIRMED (Epicor page) | D1 |
| 2.3 | UI: "add new" adds a row. "Update" finds the primary key and updates anything tied to it. | — | CONFIRMED (partner blog) | D21 |
| 2.4 | Use **Add + Update** together when loading PartWhse over a part whose default warehouse already exists, so re-writing it does not error. | — | CONFIRMED (forum, 2017, ERP 9) | D19 |
| 2.5 | On Sales Order Combined, `OrderNum` = 0 with Add New creates a new order and the system assigns the number. | `OrderNum` = `0` | CONFIRMED (forum, 2019; 2018) | D6, D7 |
| 2.6 | Required fields are enforced on update and delete as well as add (support statement). Some newer DMT versions require `PartDescription` even when only updating a part. | — | CONFIRMED (forum, 2020 and 2021) | D15, D14 |
| 2.7 | With **Update** unchecked, a kit component row still overwrote the kit's first component. | — | CONFIRMED (forum, single report, 2021) | D5 |
| 2.8 | The exact UI checkbox labels in current DMT ("Add New", "Update Existing"). | — | UNVERIFIED (D6 and D21 wording differs; no screenshot text) | D6, D21 |
| 2.9 | The message shown when Add hits an existing key. | — | UNVERIFIED (only in the excluded AI source) | — |

## 3. Required columns (answers question 6, part 1)

No public source gives an authoritative required-column list for any of these
templates. The only authoritative list is the DMT Template Builder / Required
button on the client's DMT version (1.1, 1.2), and even that is "not 100%
accurate" for combined imports (D23). The table below lists **only** columns
that a source shows were needed.

| Entity | Columns a source shows as needed | Notes | Label | Source |
|--------|----------------------------------|-------|-------|--------|
| Customer | `Company`, `CustNumCustID`, `Name` (used to **update** a default ShipTo field through the Customer DMT) | Add-new required list: UNVERIFIED. `TerritoryID` must match an existing territory code exactly (`USA` worked; `U.S.A.` failed). | Update set CONFIRMED (forum, 2021); add list UNVERIFIED | D24, D18 |
| ShipTo | `Company`, `CustNumCustID`, `ShipToNum` (plus `Name` in the working file) | `CustNumCustID` is required: its absence gave "column CustNumCustID is missing" / "Column 'CustNumCustID' does not belong to table". The default ShipTo (blank `ShipToNum`) cannot be updated through ShipTo DMT. | CONFIRMED (forum, 2017/2020/2021) | D10, D11, D24 |
| Part | `PartNum`, `PartDescription` (required even on update); UOM fields (`IUM`, `PUM`, `SalesUM`) must hold UOMs that exist in the UOM class; `ClassID` must be a code | The Part template sets the default plant and warehouse, so give valid Plant/Warehouse codes (2017, ERP 9). Other required columns (`TypeCode` etc.): UNVERIFIED. | CONFIRMED (forum) for listed items | D14, D15, D13, D19 |
| PartPlant | `Company`, `PartNum`, `Plant`, `PrimWhse` | `PrimWhse` is required ("Warehouse is required") and must exist in that site. `Company`, `PartNum` and `Plant` as keys are UNVERIFIED (inferred from the table key). | `PrimWhse` CONFIRMED (forum, 2025); keys UNVERIFIED | D9 |
| PartWhse | `Company`, `PartNum`, `Plant`, `WarehouseCode`, `BinNum` (one ERP 9 file header) | That header was not labeled as PartWhse in the thread; current required list UNVERIFIED. | UNVERIFIED (the only evidence is an unlabeled 2017 ERP 9 header) | D19 |
| Sales Order Combined | 10.1.600 order (Simon Hall): 1 `Company`, 2 `OrderNum`, 3 `CustomerCustID`, 4 `OrderDtl#OrderLine`, 5 `OrderDtl#PartNum`, 6 `OrderDtl#LineDesc`, 7 `OrderDtl#SellingQuantiy` (spelling as posted), 8 `OrderRel#OrderRelNum`. Rows 4–8 optional. | `CustomerCustID`: "DMT says it is required but does not actually enforce it" (D8). Kinetic 2025 suggestion: `Company,OrderNum,CustNum,PONum,RequestDate,OrderDate,CustomerCustID,OrderDtl#Company,OrderDtl#OrderLine,OrderDtl#PartNum,OrderRel#Company,OrderRel#OrderNum,OrderRel#OrderLine,OrderRel#OrderRelNum` (not confirmed as working). Unit price: `OrderDtl#DspUnitPrice` loaded where `DocUnitPrice` loaded 0 (D22). | 10.1.600 list CONFIRMED (forum, 2018); Kinetic required list UNVERIFIED | D8, D3, D22 |

Sales Order Combined line rules (CONFIRMED, forum):
- Rows sharing an order need distinct `OrderDtl#OrderLine` values. Restarting at 1 starts a new order (D6, 2019).
- With `OrderNum` = 0, OrderLine values were not preserved; the next line number was used (D6).
- Kits use up line numbers for their components. Leave gaps larger than the kit (1, 21, 41), or 1, 2, 15 for an 11-component kit, and set components' `KitFlag` = `C` (D5).
- If the customer has duplicate-PO checking on, a new order number is assigned at each PONum change (D6, D7).

## 4. Load order

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 4.1 | Load parents before children, as in manual entry: Customer, then Contact. | CONFIRMED (forum, 2018) | D23 |
| 4.2 | Customer before ShipTo, and Customer and Part before Sales Order. | UNVERIFIED as a stated rule. It follows from the lookups (`CustNumCustID`, `CustomerCustID`, `OrderDtl#PartNum`) needing the record to exist (1.5), but no source states the order. | — |
| 4.3 | Part, then PartPlant, then PartWhse (separate templates preferred over combined). | CONFIRMED (forum, 2017, ERP 9) | D19 |
| 4.4 | New-part order: Part, PartPlant, PartRev, PartOpr, PartMtl. | CONFIRMED (forum, 2017) | D20 |
| 4.5 | Part revisions before Part. | CONFLICTING: one poster had to load PartRevs before Parts (D14, 2021) vs Part before PartRev (D20, 2017) | D14, D20 |
| 4.6 | UOM classes and UOM conversions must exist before Part. | CONFIRMED (forum, 2023) | D13 |
| 4.7 | The warehouse must be set up and valid in the site before PartPlant. | CONFIRMED (forum, 2025) | D9 |
| 4.8 | DMT **Migration Mode** "helps define the order in which imports should be used when migrating"; running imports in menu order helps load data in the right sequence. | CONFIRMED (Epicor page) | D1 |
| 4.9 | PlayList **Wait** makes DMT finish one import before starting the next. | CONFIRMED (Epicor page) | D1 |

## 5. Error log format

| # | Claim | Exact value | Label | Source |
|---|-------|-------------|-------|--------|
| 5.1 | Row errors show as `Table: <TableName> Msg: <message>` (the separator was a `;` in one quote). | `Table: PartPlant Msg: Warehouse is required.`; `Table; Customer Msg: You do not have permissions to this record.` | CONFIRMED (forum, 2025 and 2021) | D9, D18 |
| 5.2 | DMT keeps three logs, each of which can be switched off: Complete Log (`-NoCompleteLog`), Error Log (`-NoErrorLog`), Error Input Log (`-NoErrorInput`). `-LogDetailedException` adds the detailed exception to the error log. | — | CONFIRMED (GitHub wiki, 2021) | D2 |
| 5.3 | Since about Nov 2019 the error file (`error.txt`) uses several lines per error instead of one line. This makes it harder to match errors back to input rows. Epicor ticket PRB0214446. | — | CONFIRMED (forum, 2019) | D15 |
| 5.4 | Logs are "usually in the same folder as the original input file". | — | CONFLICTING: stated by one poster; the asker found "Nothing there" (D17, 2019) | D17 |
| 5.5 | Clicking View before the run finishes gave "File does not exist". | — | CONFIRMED (forum, 2019) | D17 |
| 5.6 | Automated (`-NoUI`) runs write `DMT_NoUIImport_Error.log`. No switch stopped it (2022). | — | CONFIRMED (forum, 10.2.700.15) | D16 |
| 5.7 | The UI option "Write errors to log" records one message per bad row. | — | CONFIRMED (partner blog) | D21 |
| 5.8 | Exact file names, columns and delimiter of the Error Input Log in current DMT. | — | UNVERIFIED | — |

## 6. Top 15 failure messages (answers question 6, part 2)

These are the 15 verbatim messages found, with entity and fix. **No source ranks
them by frequency**, so "top 15" means "15 cited", not "15 most common". The
frequency ranking is UNVERIFIED.

| # | Entity | Verbatim message | Cause / fix | Date, release | Source |
|---|--------|------------------|-------------|---------------|--------|
| 1 | PartPlant | `Table: PartPlant Msg: Warehouse is required.` | Fill `PrimWhse` with a warehouse valid in that site | 2025-03-28 | D9 |
| 2 | ShipTo | `Column 'CustNumCustID' does not belong to table.` | Add `CustNumCustID` and fill it with Customer.CustID | 2017-08-25, ERP 10 | D10 |
| 3 | ShipTo | `column CustNumCustID is missing` (as quoted by poster) | Same as #2 | 2020-10-02, ERP 10 | D11 |
| 4 | ShipTo (default) | `Not allowed to update default ShipTo` | Default ShipTo (blank ShipToNum) can't be updated through ShipTo DMT; use Customer DMT | 2021-11-09, ERP 10 | D24 |
| 5 | Customer | `Table; Customer Msg: You do not have permissions to this record.` | Territory Security: give the user "View All Territories" in Workforce, or assign territories; match TerritoryID exactly | 2021-10-13, Kinetic category | D18 |
| 6 | CustNumCustID lookup (HDCase) | `Invalid Sold To` | Hidden carriage return after the CustID value | 2023-02-25, Kinetic category | D12 |
| 7 | Part | `Primary Unit of measure for Inventory not found for Class:COUNT UOM:EA` | UOM code wrong (`EACH`, not `EA`) or not in class | 2023-08-28 | D13 |
| 8 | Part | `Primary Unit of measure for Purchasing not found for Class:COUNT UOM:EA` | Same as #7 | 2023-08-28 | D13 |
| 9 | Part | `Primary Unit of measure for Sales not found for Class:COUNT UOM:EA` | Same as #7 | 2023-08-28 | D13 |
| 10 | Part | `Unit Net Volume Unit of measure not found for Class:VOLUME UOM:GA` | Add the missing UOM to the class | 2023-08-28 | D13 |
| 11 | Part | `Unit of measure not found for Class:LENGTH UOM:FT` | Add the missing UOM to the class | 2023-08-28 | D13 |
| 12 | Part | `Field references invalid value` (also posted as "Field Reference Invalid Value") | Code vs description (`FG`), case of plant/warehouse IDs; in one case PartRevs had to load first | 2021-05-06, ERP 10 | D14 |
| 13 | Sales Order Combined | `Invalid OrderRelNum` (last line of a multi-line order) | Unresolved; suggestions: include all `OrderRel#` key columns, move OrderRel columns to the end | 2025-09-12 | D3 |
| 14 | Sales Order Combined | `Invalid Column name 'OrderRelNum'` | Moving the `OrderRel#` columns to the end stopped it | 2025-09-15 | D3 |
| 15 | Sales Order Combined | `Input array is longer than the number of columns in this table` | No confirmed fix; suggestions: separate header and line files, explicit OrderNum, check UOM on every line | 2018-11-21, DMT 4.0.36 / 10.2 | D7, D8 |

Entities with no verbatim message found: Customer **add** errors (other than #5)
and PartWhse. UNVERIFIED.

## 7. CLI switches

Switch descriptions below are quoted from D2 (GitHub wiki, last modified
2021-09-03, DMT version not stated). CONFIRMED (GitHub wiki) unless noted.

| Switch | Description (verbatim from D2) |
|--------|--------------------------------|
| `-User` | "Specifies the username to connect with" |
| `-Pass` | "Specifies the password to connect with" |
| `-ConfigValue` | "Specifies which config file should be used, if not specified then default.sysconfig is assumed" |
| `-sso` | "Specifies Single Sign On" |
| `-LogDetailedException` | "Specifies if the detailed exception should be included in the error log file. Valid values are True or False." |
| `-NoUI` | "This will run DMT without a User Interface, this supports being run from a scheduled task" |
| `-Add` | "Indicates that records should be added" |
| `-Update` | "Indicates that records should be updated" |
| `-Delete` | "Indicates that records should be deleted" |
| `-Trace` | "This will enable tracing in Epicor" |
| `-LoadViaOdbc` | "Forces DMT to use ODBC to read import data, use if errors occur on data load" |
| `-ExportData` | "Exports format of all imports to specified file" |
| `-ExportDataFormat` | "Set to xml to export imports to xml rather than csv" |
| `-Delimiter` | "Sets delimiter for import files" |
| `-Import` | "Specifies the Import to run" |
| `-Source` | "Specifies the import source file" |
| `-Converter` | "Specifies the location of an assembly containing a method to convert the data before importing" |
| `-NoCompleteLog` | "When set to TRUE this will disable the Complete Log" |
| `-NoErrorLog` | "When set to TRUE this will disable the Error Log" |
| `-NoErrorInput` | "When set to TRUE this will disable the Error Input Log" |
| `-PlayList` | "Executes PlayList through command line with specified import source file" |
| `-PlayBook` | "Executes PlayBook through command line with specified import source file" |
| `-Export` | "When Export is set and Import is not, this tells DMT to perform a BAQ Export." |
| `-BAQ` | "The name of the BAQ to run in BAQ Export mode." |
| `-Target` | "The file path of the output file to create in BAQ Export Mode." |
| `-PageSize` | "The number of records to read from the BAQ at a time. Larger = faster. Smaller = less memory. Default 10000." |
| `-UseFieldNames` | "Include this flag to use the BAQ Field Name rather than Field Label." |

Additional CLI facts:
- Epicor's sample BAQ export: `start C:\Epicor\ERP10\DMT.exe -User=myuser -Pass=mypass -Export -BAQ="CustomerExport" -Target="C:\CustExport.csv"`. CONFIRMED (Epicor page) — D1.
- A PlayList is "a comma separated list of Command Line Arguments with the name of the argument in the header". CONFIRMED (Epicor page) — D1.
- `-ConnectionUrl`, `-Server`, `-Port`: UNVERIFIED (not in D2; seen only in search snippets).
- `DMT.exe /?` lists the switches for the installed version: UNVERIFIED (search snippet only). The authoritative source is Epicor's "DMT Command Line Interface Lab" PDF on EpicWeb (gated).
- Whether switches take `=True` or are bare flags (`-NoUI` vs `-NoUI=True`): UNVERIFIED (sources differ in snippets).

---

## Gated / unreachable sources (for this file)

Linked from Epicor's public DMT page (D1) but hosted on EpicWeb (login required), so not read:
- DMT Quick Start Guide — https://epicweb.epicor.com/doc/Docs/DMT%20Quick%20Start%20Guide.pdf
- DMT Troubleshooting — https://epicweb.epicor.com/doc/Docs/DMT%20Troubleshooting.pdf
- DMT Command Line Interface Lab — https://epicweb.epicor.com/doc/Docs/DMT%20Command%20Line%20Interface%20Lab.pdf
- DMT PlayLists and PlayBooks Lab — https://epicweb.epicor.com/doc/Docs/DMT%20PlayLists%20and%20PlayBooks%20Lab.pdf
- DMT Templates (ZIP) — https://epicweb.epicor.com/doc/Docs/DMT%20Templates.zip
- DMT Server Processing 2024.1 — https://epicweb.epicor.com/doc/Docs/DMT%20Server%20Processing%202024.1.pdf
- DMT Installation Guide, DMT Diff Lab, DMT Labs (ZIP) — same EpicWeb path.

Also not reached: EpicCare (PRB0214446), Epicor DMT product page on epicor.com (HTTP 403 pattern seen on other epicor.com pages; not attempted).
