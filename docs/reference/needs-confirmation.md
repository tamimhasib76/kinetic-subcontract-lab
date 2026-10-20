# Needs Confirmation

Every CONFLICTING or UNVERIFIED item from `01-ssrs-forms.md`, `02-baq.md`,
`03-dmt.md` and `04-cloud-rules.md`, written as a yes/no or pick-one question.
The item reference points to the file and row where the evidence is.
Research date: 2026-10-20. Triage added 2026-10-20.

## Buckets

- **A — Decide now.** A default is proposed below (the conservative or most-cited option). The project owner approves or overrides it.
- **B — Verify on first job.** The mock shows a warning banner. No decision now.
- **C — Out of scope.** Only affects deferred skills (BPM, BAQ parameters, CTE/UnionAll, dashboards, Functions). Parked.

Triage rules applied:
- Anything about exact Kinetic screen behavior is B, not A.
- Anything that changes what Phase 2a or Phase 3 builds is A or B, never C.

## Summary

| Bucket | Count |
|--------|-------|
| A — Decide now (approved 2026-10-20) | 28 |
| B — Verify on first job | 45 |
| C — Out of scope | 8 |
| Answered | 1 (P1) |
| **Total** | **82** |

### Bucket A: approved defaults

All 28 defaults below were **approved by the project owner on 2026-10-20**
(`decisions.md`). Banner = **Yes** means the default describes Epicor behavior,
so the mock must show: **"Default chosen for the lab, not confirmed against
Epicor."** Banner = No means the default is lab design only.

| # | Question (short) | Approved default | Reason | Banner |
|---|------------------|------------------|--------|--------|
| P2 | Base acknowledgment RDD ID is `OrderAck`? | Mock uses `OrderAck`, with a banner. | Only name in sources (S1, S24); matches lab naming. | Yes |
| 7 | "Definition" relation = inner join? | Yes. Mock: Definition = inner join, Output = left outer join. | Most-cited behavior (S14); conservative because it shows row loss. | Yes |
| 9 | RDD column limit ~1,048? | Mock does not enforce a limit. Labs teach "exclude unused columns". | Limit not confirmed; excluding columns is cited good practice (S13). | Yes |
| 14 | RptLabels columns same for every report? | No. Mock gives each report its own `RptLiterals*` set plus `RptLanguageID`. | S19 shows report-specific literal columns. | Yes |
| 15 | RptParameter always has `Company`? | Mock omits it; no lab query may depend on it. | Unconfirmed; safer not to rely on it. | Yes |
| 16 | RptParameter always has `ReportID`? | Mock omits it; no lab query may depend on it. | Unconfirmed; safer not to rely on it. | Yes |
| 18 | `OrderNum` link + `ProjManager_c` → `OrderNum_ProjManager_c`? | Yes. Mock follows `<LinkKey>_<Field>`. | Pattern confirmed (S12, S16); Phase 3 gate. | Yes |
| 19 | Underscores in UD names misparsed? | Mock UD field names use no underscores except the `_c` suffix. | Avoids the reported risk at no cost. | No (lab design) |
| 20 | Un-excluded column appears only in new runs? | Yes. Mock adds the column to staging only for runs generated after the RDD save. | Staging tables are created per run (S13, S14). | Yes |
| 22 | RDL namespace for mock RDLs? | Author mock RDLs in the 2016/01 namespace. Banner: cloud may reject it (S30). | Report Builder 2016 upgrades older files on open (S31), so 2010 cannot be kept. | No (lab design; item 22 keeps its own cloud banner) |
| 25 | PackSlip RDD ID is `PackSlip`? | Mock uses `PackSlip`, with a banner. | Most likely name; only "Pack Slip RDD" is cited (S8). | Yes |
| 35 | `convert(int, datediff(...))` valid? | Yes. Mock treats it as valid T-SQL. | Standard T-SQL; it was entered without a syntax error (B11). | Yes |
| 37 | Reference another calc field: bare name or `Calculated_`? | Labs never reference one calculated field from another; repeat the expression. | Conflicting evidence (B8); avoiding it is conservative. | No (lab design) |
| 38 | Changing only the data type fixes integer division? | No. Answer key requires CAST. | M1: integer/integer truncates; B10. | Yes |
| 39 | `* 1.0` forces decimal division? | Mock accepts it, but the answer key uses CAST. | M1 type precedence supports it; CAST is the cited fix (B9). | Yes |
| 46 | Calc expression inserted verbatim into SELECT? | Yes. Mock inserts the expression text verbatim. | Simplest model consistent with B12 ("enter only the expression"). | Yes |
| 49 | `#` means `<ChildTable>#<Field>`? | Yes. Mock parses headers that way. | Every cited combined header fits (D3, D4, D7, D8). | Yes |
| 53 | `TypeCode` required on Part? | Mock warns if it is missing; it does not fail the row. | Unconfirmed; a warning avoids a false failure. | Yes |
| 54 | `Company`, `PartNum`, `Plant` required on PartPlant? | Yes. Mock fails rows without them. | Table key; conservative. | Yes |
| 55 | PartWhse requires `Company`, `PartNum`, `Plant`, `WarehouseCode`? | Yes. Mock fails rows without them. | Only cited header (D19); conservative. | Yes |
| 57 | `CustomerCustID` required on Sales Order Combined? | Yes. Mock fails rows without it. | DMT labels it required (D8); conservative even though not enforced. | Yes |
| 58 | Customer before ShipTo? | Yes. Mock rejects a ShipTo whose customer is not loaded. | Parent-first rule (D23); `CustNumCustID` lookup (D11). | Yes |
| 59 | Customer and Part before Sales Order Combined? | Yes. Mock rejects orders that reference unloaded records. | Lookups need existing records (D8). | Yes |
| 60 | Part or PartRev first? | Part first. | Two sources (D19, D20) plus the parent-first rule (D23) vs one (D14). | Yes |
| 69 | SSRS own SQL data source on multi-tenant cloud? | No. Treated as blocked. | "Not a supported Epicor configuration" (C1); lab rule 1. | Yes |
| 70 | SQL views as RDD data sources? | No. Not allowed in labs. | No source shows it; conservative. | Yes |
| 71 | Cloud user queries `<Table>_<GUID>` tables directly? | No. Not allowed in cloud labs. | No direct SQL in cloud (C2); conservative. | Yes |
| 75 | SSRS stored-procedure dataset on multi-tenant cloud? | Blocked. | Follows from no direct SQL (C2, C1); lab rule 1. | Yes |

## Standing first-ticket questions (ask on every new client)

| # | Question | Answer type | Bucket |
|---|----------|-------------|--------|
| a | Which Report Builder version matches the client's SSRS server? (RB 3.0 / 2016 / 2019 / other) | pick one | B |
| b | Does Publish in SSRS Report Design save to the report style on this release? | yes / no | B |
| c | What is the exact base dataset query in the client's downloaded RDL? (attach the query text) | paste | B |
| d | What is the client's Kinetic release and deployment? (on-prem / public cloud / private cloud + exact build) | pick one + build | B |
| e | Which RDD does the base style of each form in the ticket use? (e.g. AR_Form → ARInvoice or ARForm) | pick one per form | B |

## Project owner questions

| # | Question | Answer type | Bucket | Ref |
|---|----------|-------------|--------|-----|
| P1 | What are the five existing Phase 2b fix-drill defects? | list | Answered 2026-10-20 (`decisions.md`, `02-baq.md`) | 02 "Phase 2b fix-drill defects" |
| P2 | Is the lab's base RDD ID for the acknowledgment form exactly `OrderAck`? | yes / no | A | 01 Naming; (5) |

## 01 — SSRS forms

| # | Question | Answer type | Bucket | Ref |
|---|----------|-------------|--------|-----|
| 1 | Which release first used `ARInvoice` for the base AR_Form style? (2023 / 2024.1 / other) | pick one | B | 01 Naming, 1.9 (S18 vs S35) |
| 2 | On 2025.2 cloud, does a downloaded base AR invoice RDL point to `ARInvoice`? | yes / no | B | 01 Naming (S36) |
| 3 | Does the Copy Report Style dialog ask for a new style number? | yes / no | B | 01 1.7 |
| 4 | Does the Copy Report Style dialog ask for a description? | yes / no | B | 01 1.7 |
| 5 | Does upload reject a Report Location outside `reports/CustomReports`? | yes / no | B | 01 2.9, 7d |
| 6 | Is the Kinetic field labeled exactly "Report Location"? | yes / no | B | 01 2.10 |
| 7 | Does a "Definition" relationship produce an inner join in Kinetic 2022+? | yes / no | A | 01 3.15 |
| 8 | Which Relation Type values does the Kinetic RDD offer? (Output / Definition / Definition Only / other) | pick all that apply | B | 01 3.18 |
| 9 | Is there an RDD column-count limit near 1,048? | yes / no | A | 01 3.19 |
| 10 | Does Generate for Design work for non-BAQ custom SSRS reports? | yes / no | B | 01 4.4 |
| 11 | On 2025.2.16, does Publish save the changed RDL without a manual zip upload? | yes / no | B | 01 6.9 |
| 12 | Does Report Style zip upload work from the browser (with Edge Agent)? | yes / no | B | 01 7.11 |
| 13 | On cloud 2025.2, does a zip upload reliably replace the RDL? | yes / no | B | 01 7.12 |
| 14 | Does RptLabels_<GUID> have the same columns for every report? | yes / no | A | 01 (1) |
| 15 | Does RptParameter_<GUID> always contain `Company`? | yes / no | A | 01 (1) |
| 16 | Does RptParameter_<GUID> always contain a `ReportID` column? | yes / no | A | 01 (1) |
| 17 | Are RptParameter option columns (e.g. `DetailCarbonCost`) controlled by RDD exclusions? (RDD exclusions / licensing / other) | pick one | B | 01 (1) |
| 18 | Does a link on `OrderNum` that picks `ProjManager_c` produce the staging column `OrderNum_ProjManager_c`? | yes / no | A | 01 (2) |
| 19 | Are underscores inside UD field names misparsed as a link separator? | yes / no | A | 01 (2) |
| 20 | Does an un-excluded column appear only in runs generated after the RDD is saved? | yes / no | A | 01 (2) |
| 21 | Does the `BAQReportParameter_<GUID>` table still exist in Kinetic 2022+? | yes / no | B | 01 (3) |
| 22 | Which RDL namespace do standard Kinetic RDLs use? (2008/01 / 2010/01 / 2016/01) | pick one | A (mock authoring default); client value verified via c | 01 (4) |
| 23 | Does Report Builder 2016 save a 2016-namespace Kinetic RDL without changing the namespace? | yes / no | B | 01 (4) |
| 24 | Does Kinetic 2022+ cloud accept an RDL with the 2016/01 namespace? | yes / no | B | 01 (4); 04 1.21 |
| 25 | Is the standard Pack Slip RDD ID exactly `PackSlip`? | yes / no | A | 01 (5) |
| 26 | Is the base PackSlip main query `ShipHead_ T1 LEFT OUTER JOIN ShipDtl_ T2 ON Company, PackNum` + `RptLabels_ T3 ON RptLanguageID`? | yes / no | B (Phase 3 gate: pattern only; see `decisions.md`) | 01 (5) |
| 27 | Is the OrderAck main dataset named `OrderHed` with OrderHed aliased `T1`? | yes / no | B (Phase 3 gate) | 01 (5) |
| 28 | Does the ARInvoice/ARForm main query start `FROM InvcHead_ T1` joined to `InvcDtl_ T2`? | yes / no | B | 01 (5) |
| 29 | Can the full relationship list of each of the three RDDs be exported from the RDD screen? | yes / no | B | 01 (5) |

## 02 — BAQ

| # | Question | Answer type | Bucket | Ref |
|---|----------|-------------|--------|-----|
| 30 | Is `RecursiveCTE` a separate subquery type value? | yes / no | C | 02 1.1 |
| 31 | Do `Intersect` and `Except` subquery types exist? | yes / no | C | 02 1.2 |
| 32 | Must a Union/UnionAll subquery roll up to a TopLevel or CTE? | yes / no | C | 02 1.8 |
| 33 | Which join types does the Kinetic relation editor offer? (inner / left / right / full / cross) | pick all that apply | B | 02 2.3 |
| 34 | Can a default join in a UnionAll subquery silently change CTE results? | yes / no | C | 02 2.5 |
| 35 | Does `convert(int, datediff(...))` run without error in a calculated field? | yes / no | A | 02 4.6 |
| 36 | Which functions are listed in the Kinetic Calculated Field editor's Data and Functions panel? (attach list) | paste | B | 02 4.10; (8) |
| 37 | To reference another calculated field, which form works? (bare name / `Calculated_<Name>` / either) | pick one | A | 02 4.11 |
| 38 | Does changing only a calculated field's data type to decimal (no CAST) fix integer division? | yes / no | A | 02 Integer division |
| 39 | Does `* 1.0` in a BAQ calculated field force decimal division? | yes / no | A | 02 Integer division |
| 40 | Does choosing "specified parameter" (not "specified expression") make parameters selectable in table criteria? | yes / no | C | 02 5.5 |
| 41 | On 2025.2, can criteria be set on two different tables in one subquery? | yes / no | B | 02 5.6 |
| 42 | Where is the Query Phrase shown in the Kinetic web designer? (Summary / General / other) | pick one | B | 02 6.1 |
| 43 | Does the Kinetic web designer generate the same SQL as Classic for the same BAQ? | yes / no | B | 02 6.6 |
| 44 | Can SQL be pasted into the BAQ designer to create a BAQ? | yes / no | B | 02 6.7 |
| 45 | Are `Constants.*` and `@Param` replaced with values before the SQL runs? | yes / no | B (`Constants.Today` may appear in the date-field drill; `@Param` part is deferred) | 02 6.8 |
| 46 | Is the calculated field expression inserted verbatim into the generated SELECT list? | yes / no | A | 02 6.9; (8) |
| 47 | Does `RemoveTestRowLimit` = TRUE lift the 10,000-row cap in the designer's test run? | yes / no | B | 02 7.7 |
| 48 | What are the exact Kinetic button labels for Analyze and Test? (paste labels) | paste | B | 02 7.10 |

## 03 — DMT

| # | Question | Answer type | Bucket | Ref |
|---|----------|-------------|--------|-----|
| 49 | Does `#` in a combined-template header mean "<ChildTable>#<Field>"? | yes / no | A | 03 1.4 |
| 50 | Are the DMT UI checkboxes labeled "Add New" and "Update Existing"? | yes / no | B | 03 2.8 |
| 51 | What message does DMT show when Add hits an existing key? (paste text) | paste | B | 03 2.9 |
| 52 | Which columns does the Customer template's Required button list on the client's DMT version? (paste) | paste | B | 03 §3 Customer |
| 53 | Is `TypeCode` required on the Part template? | yes / no | A | 03 §3 Part |
| 54 | Are `Company`, `PartNum`, `Plant` required on PartPlant? | yes / no | A | 03 §3 PartPlant |
| 55 | Is the PartWhse required set `Company`, `PartNum`, `Plant`, `WarehouseCode`? | yes / no | A | 03 §3 PartWhse |
| 56 | Which columns does the Sales Order Combined Required button list on the client's DMT version? (paste) | paste | B | 03 §3 Sales Order Combined |
| 57 | Is `CustomerCustID` enforced as required on Sales Order Combined? | yes / no | A | 03 §3 (D8) |
| 58 | Must Customer load before ShipTo? | yes / no | A | 03 4.2 |
| 59 | Must Customer and Part load before Sales Order Combined? | yes / no | A | 03 4.2 |
| 60 | Load order for part data: which comes first? (Part / PartRev) | pick one | A | 03 4.5 |
| 61 | Are DMT logs written to the input file's folder? | yes / no | B | 03 5.4 |
| 62 | What are the Error Input Log's file name, columns and delimiter on the client's DMT version? (paste a sample) | paste | B | 03 5.8 |
| 63 | Which DMT failure messages are most frequent on this client? (rank the 15 in §6) | rank | B | 03 §6 |
| 64 | Which error messages appear for Customer add and PartWhse loads? (paste) | paste | B | 03 §6 |
| 65 | Does the client's DMT support `-ConnectionUrl`? | yes / no | B | 03 §7 |
| 66 | Does the client's DMT support `-Server` and `-Port`? | yes / no | B | 03 §7 |
| 67 | Does `DMT.exe /?` list all switches on the client's version? | yes / no | B | 03 §7 |
| 68 | Are flags written bare or with a value? (`-NoUI` / `-NoUI=True`) | pick one | B | 03 §7 |

## 04 — Cloud rules

| # | Question | Answer type | Bucket | Ref |
|---|----------|-------------|--------|-----|
| 69 | Does an SSRS report with its own SQL data source run on the client's multi-tenant cloud? | yes / no | A | 04 1.2 |
| 70 | Can SQL views be added as RDD data sources? | yes / no | A | 04 1.5 |
| 71 | Can a cloud user query the `<Table>_<GUID>` report tables directly? | yes / no | A | 04 1.6 |
| 72 | Can `Sandbox.IO` write to a `FileShare` folder? | yes / no | C | 04 1.9 |
| 73 | First release where `this.Sandbox.IO` works? (2024.2 / 2025.1 / 2025.2) | pick one | C | 04 1.10 |
| 74 | Are Function libraries that use restricted features disabled after an upgrade? | yes / no | C | 04 1.12 |
| 75 | Is an SSRS stored-procedure dataset blocked on multi-tenant cloud? | yes / no | A | 04 1.17 |

---

## Gated or unreachable sources (all four files)

| Source | Why unreachable | Needed for |
|--------|-----------------|-----------|
| Epicor Kinetic Application Help (Report Style, Report Data Definition, SSRS Report Design, System Monitor, BAQ Designer) | No public URL found; in-product help | 01, 02 |
| Kinetic help topic "Accessing Resources Using the Sandbox Property" | Cited second-hand in C7; no public URL found | 04 |
| EpicWeb — Kinetic BAQ Designer User Guide / ICE Tools User Guide | Login required | 02 |
| Scribd copy of "Kinetic BAQ Designer User Guide" (https://www.scribd.com/document/720590765/Kinetic-BAQDesignerUserGuide) | Page body failed to load | 02 |
| EpicWeb — DMT Quick Start Guide, DMT Troubleshooting, DMT Command Line Interface Lab, DMT PlayLists and PlayBooks Lab, DMT Templates (ZIP), DMT Server Processing 2024.1, DMT Installation Guide, DMT Diff Lab, DMT Labs (ZIP) — https://epicweb.epicor.com/doc/Docs/ | Login required | 03 |
| EpicCare knowledge base and cases (CS0005452645, PRB0214446) | Login required | 01, 03 |
| epicor.com BAQ product page | HTTP 403 to WebFetch | 02 |
| epicor.com Cloud SDK page | HTTP 403 to WebFetch | 04 |
| Epicor cloud SaaS service description / customer policy documents | Not found publicly; login required | 04 |
| Epicor staff GitHub gist of Sandbox.IO methods (https://gist.github.com/Epic-Santiago/b842d06370cb56d2b1af43ae1f45f5e8) | Seen in search results; not fetched | 04 |
