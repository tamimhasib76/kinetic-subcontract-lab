# DMT pre-load validator kit

A file-only kit for checking a DMT batch before anyone loads it. No database, no
Epicor connection. It reads CSVs and writes a remediation report.

Source of truth: `docs/reference/03-dmt.md`, `docs/reference/decisions.md`, and the
approved bucket A defaults in `docs/reference/needs-confirmation.md`. Source IDs in
findings (`[D9]`, `[M3]`) are the IDs in `03-dmt.md` and `02-baq.md`.

## Contents

| Path | What it is |
|------|------------|
| `validate_dmt.py` | Standalone Python/pandas CLI. Writes `dmt-remediation.html` and `dmt-remediation.csv`. |
| `validation-queries.sql` | The same checks as a SQL Server script for a staging database. Text only: it has not been run in this kit. |
| `sample-dirty-csvs/` | A fictional manufacturer with two companies, MFG01 and MFG02, that share some CustIDs and PartNums. About 100 rows per file, with 15 planted errors. |
| `sample-dirty-csvs/reference/` | Setup data the batch is checked against: `sites.csv` (Company, Plant, WarehouseCode) and `uom.csv` (Company, UOMClassID, UOMCode). |
| `sample-dirty-csvs/load-plan.csv` | The planned load order (Seq, Entity, File). |

The answer key is not in the repo. It is in `/answers/`, which is git-ignored.

## Run it

```bash
pip install pandas
cd dmt-validator
python validate_dmt.py --data sample-dirty-csvs --out reports
# open reports/dmt-remediation.html; reports/dmt-remediation.csv is the work list
```

Options:

- `--data`: folder holding the six CSVs, `reference/` and `load-plan.csv`.
- `--out`: output folder (default `reports`).
- `--date-format`: the `strptime` format every date must match (default `%Y-%m-%d`).
- `--mode add|update`: the action for the whole run. Required for files without a
  `LabAction` column (see below).
- `--before [ENTITY=]FILE`: a before-image, i.e. an export of the records already in
  the target. It needs at least the entity's key columns. You can repeat it, once per
  entity. Name the entity (`--before Part=part-export.csv`) or let the file name say
  it (`Customer-before.csv`).

The script prints the error, warning and note counts. It returns exit code 1 if there
is at least one ERROR, or if `--mode` is needed but not given, so it can gate a script.

On the sample files it reports **15 errors, 0 warnings**. Those are the 15 planted
errors, matched on file, row and check.

## Lab mode and run mode (real client files)

DMT sets Add or Update per import run (`-Add`, `-Update`, PlayLists: 03-dmt.md 2.1,
2.2), not per row. The validator supports both ways of saying it, file by file:

| | Lab mode | Run mode |
|---|----------|----------|
| When | The file has a `LabAction` column (the samples) | The file has no `LabAction` column (real client files) |
| Action | `LabAction` per row; `--mode` is ignored for that file (an INFO note says so) | `--mode add` or `--mode update` for every row. Without `--mode` the run stops with an error |
| Key-change check | Each Update row's key is compared with its `LabTargetKey` | `--mode add`: does not apply. `--mode update` with `--before`: an Update row whose key is not in the before-image is reported as `UPDATE_KEY_CHANGE` (a changed key, or a record that does not exist [D21]). `--mode update` without `--before`: **not checked**, and the report carries a `KEY_CHANGE_NOT_CHECKED` note asking for a before-image |
| Parents for FK checks | Rows in the batch + records targeted by Update rows | Rows in the batch + before-image records (in either mode) |

A real DMT run loads one entity. If you validate several client files in one run
mode, every file gets the same action. Run the validator once per mode if the batch
mixes Add and Update files.

```bash
# client Add files, no lab columns
python validate_dmt.py --data client-files --mode add
# client Update file, with a before-image to catch key changes
python validate_dmt.py --data client-files --mode update --before Part=part-export.csv
```

### Test run: samples with both lab columns removed

On a copy of `sample-dirty-csvs/` with `LabAction` and `LabTargetKey` dropped from every file:

| Run | Result |
|-----|--------|
| no `--mode` | stops: "No LabAction column in ... Give --mode add or --mode update" |
| `--mode add` | **18 errors, 0 warnings, 6 notes.** 13 of the 15 planted errors are found. The 2 Update key changes cannot be seen without a before-image, as designed. The 5 extra errors (2 `FK_CUSTOMER`, 3 `FK_PART`) are knock-on effects of those 2 renamed keys: without `LabTargetKey`, rows that still use the two original keys have no parent. The 6 notes are one `KEY_CHANGE_NOT_CHECKED` per file |
| `--mode update` without `--before` | 18 errors, 6 notes saying key changes were not checked |
| `--mode update --before` (Customer and Part before-images) | 15 errors, 4 notes: the same 15 planted errors as lab mode. Both key changes are caught and the FK knock-ons go away |

## File layout

- Headers are table field names, as in plain templates (03-dmt.md 1.3, [D19]).
  Lookup columns `CustNumCustID` (ShipTo) and `CustomerCustID` (OrderHed) carry
  the CustID string (1.5, [D11][D8]).
- `OrderDtl.csv` carries release columns as `OrderRel#OrderRelNum` and
  `OrderRel#Plant`. Reading `#` as `<ChildTable>#<Field>` is approved default 49.
  **Default chosen for the lab, not confirmed against Epicor.** The field name
  `Plant` on OrderRel is not cited in the reference (UNVERIFIED). The kit uses it as
  the site the line ships from.
- `SellingQuantity` is spelled correctly. The cited 10.1.600 header is
  `OrderDtl#SellingQuantiy` (spelling as posted, [D8]). Copy headers from the
  client's Template Builder (1.1, 1.6).
- **Lab columns, not DMT columns:** `LabAction` (`Add` or `Update`) and
  `LabTargetKey` (for Update rows, the pipe-separated key of the record being
  updated, e.g. `MFG01|SABLE`). They are optional: without them, use `--mode`
  (see "Lab mode and run mode"). Split the file by action and drop both lab
  columns before loading.
- Row numbers in the report are spreadsheet rows: the header is row 1.

## What it checks

| Check | Rule | Basis |
|-------|------|-------|
| `LOAD_ORDER` | Customer before ShipTo; Part before PartPlant; Customer before OrderHed; Part before OrderDtl | Defaults 58 and 59 (banner), [D23][D11][D8]; [D19][D20] |
| `REQUIRED_MISSING` | Blank or absent: ShipTo `CustNumCustID`; Part `PartNum`, `PartDescription`; PartPlant `PrimWhse`, plus `Company`/`PartNum`/`Plant`; OrderHed `Company`, `OrderNum`, `CustomerCustID` | [D10][D11]; [D14][D15]; [D9]; default 54 (banner); [D8], default 57 (banner) |
| `OPTIONAL_MISSING` (warning) | Part `TypeCode` blank | Default 53: warn, do not fail (banner) |
| `SHIPTO_DEFAULT_UPDATE` | Update row with blank ShipToNum | [D24] |
| `UPDATE_KEY_CHANGE` | Lab mode: Update row whose key differs from `LabTargetKey`. Run mode: Update row whose key is not in the `--before` image | Update finds the record by its primary key [D21] (2.3) |
| `KEY_CHANGE_NOT_CHECKED` (note) | Run-mode file whose key changes could not be checked (Add run, or Update run with no `--before`) | Lab check |
| `WHITESPACE` | Leading/trailing spaces, tabs, CR/LF or other hidden characters in any column | [D12] (1.9) |
| `CUSTNUM_NOT_INT` | Non-integer in `CustNum` (usually a CustID typed into it) | [D10]; [M2][M3], fix-drill defect 2 |
| `CUSTNUM_MISMATCH` | OrderHed `CustNum` differs from that customer's CustNum in the same Company | Lab check; [D10] |
| `TYPE_INT`, `TYPE_DECIMAL` | OrderNum, OrderLine, OrderRelNum, SellingQuantity | Lab check |
| `BAD_DATE` | Dates not in the batch format | Lab check: the reference cites no DMT date format |
| `DUPLICATE_KEY` | Same key twice in a file | OrderDtl: [D6]. PartPlant: default 54 (banner). Others: lab key |
| `FK_CUSTOMER`, `FK_PART`, `FK_ORDERHED` | Child row references a parent not in the batch (nor targeted by an Update row). Always matched within the same Company | Defaults 58/59 (banner), [D19]; lab check for OrderHed |
| `UOM_NOT_FOUND` | Part IUM/PUM/SalesUM not in `reference/uom.csv` for the Company | [D13] |
| `SITE_UNKNOWN`, `WHSE_NOT_IN_SITE` | Plant not a site of the Company; PrimWhse not a warehouse of that site; case-sensitive | [D9]; [D14] |
| `PARTPLANT_MISSING_FOR_SITE` | Order line ships a part from a site where that Company has no PartPlant row. Names the other Company when only it has the row | Lab check (data gap); [D9][D19][D20] context |

Every finding has a `Basis` column. Findings that rest on an approved bucket A
default carry: **"Default chosen for the lab, not confirmed against Epicor."**
Missing-column findings are always worded "required per cited source [D#]".

To keep one root cause from producing several findings, lookups compare trimmed
values. A UOM of `EA ` is reported once, as WHITESPACE, not again as UOM_NOT_FOUND.
Rows with a blank key are skipped by the duplicate and foreign-key checks; the
REQUIRED check reports them.

## What it does not claim

- **It does not predict DMT behavior.** It does not say whether DMT rejects,
  skips, partly loads or changes a row that fails a check. No reference source
  covers that, and the error-log format for current DMT is UNVERIFIED (03-dmt.md 5.8).
- **The required-column lists are not complete.** The reference has no
  authoritative required list for any template (03-dmt.md §3). The only
  authoritative list is the Template Builder / Required button on the client's DMT
  version, and that is "not 100% accurate" for combined imports ([D23]). The
  Customer Add list is UNVERIFIED (question 52), so Customer has no required-column
  check.
- **Table keys are lab keys** unless a source is named. The Customer, ShipTo, Part
  and OrderHed keys are not stated in the reference.
- **Date format is a lab choice.** No cited source says which date formats DMT accepts.
- **PARTPLANT_MISSING_FOR_SITE is a data gap, not a predicted error message.**
- **A before-image comparison cannot tell a changed key from a missing record.**
  Both show as an Update key that is not in the before-image. Without `--before`,
  run-mode Update files are not checked for key changes at all.
- It does not check PartWhse, PartRev, UOM conversions, territories, prices or
  kit line numbering. It does not check that OrderHed loads before OrderDtl,
  because no source states that order.
- The SQL script is a translation of the same checks for a staging database. It
  has not been run here. Never run it against an Epicor database. On multi-tenant
  cloud there is no direct SQL at all (04-cloud-rules.md 1.1).
- No Epicor screenshots, logos or copied help text are used. All data is fictional.
