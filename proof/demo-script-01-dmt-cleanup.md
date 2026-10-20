# 5-Minute Demo Script 01: Pre-Load DMT Batch Validation & Remediation

> **Notice**: Lab exercise on synthetic data. Not client work.
>
> **Synthetic Lab Disclosure**: Uses synthetic lab files in [`dmt-validator/sample-dirty-csvs/`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/dmt-validator/sample-dirty-csvs). No SQL Server or Epicor connection is used.
> **Lab Banner**: *"Default chosen for the lab, not confirmed against Epicor."*

---

## Timing & Pacing Overview (Total: 5:00)

| Segment | Time | Screen / Artifact Shown | Objective |
|---| :---: |---|---|
| **1. Framing & Scope** | `0:00 – 0:45` | Terminal + `load-plan.csv` | Explain file-only pre-load checks across the 6 entity CSVs before touching DMT. |
| **2. Live Validator Run** | `0:45 – 1:45` | Terminal CLI output | Run `validate_dmt.py` and review the `15 errors, 0 warnings` summary by check type. |
| **3. HTML Report Walkthrough** | `1:45 – 3:30` | [`proof/reports/dmt-remediation.html`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/reports/dmt-remediation.html) | Inspect 4 high-impact findings (`LOAD_ORDER`, `CUSTNUM_NOT_INT`, `UPDATE_KEY_CHANGE`, `PARTPLANT_MISSING_FOR_SITE`). |
| **4. Remediation & Re-Run** | `3:30 – 5:00` | Terminal CLI output (`0 errors`) | Show how fixing the CSVs and load order produces a clean `0 errors, 0 warnings` verification run. |

---

## Minute-by-Minute Script

### `0:00 – 0:45` · 1. Framing the Pre-Load Check
- **Action**: Show the directory listing of `dmt-validator/sample-dirty-csvs/`.
- **Talk Track**:
  - *"This is a synthetic two-company (`MFG01`, `MFG02`) cutover batch of six CSVs (`Customer`, `ShipTo`, `Part`, `PartPlant`, `OrderHed`, `OrderDtl`), site/UOM reference extracts, and `load-plan.csv`."*
  - *"Before opening DMT on a workstation, we run `validate_dmt.py` offline. It never connects to Epicor or SQL Server, and every finding cites its source (`[D#]` in `03-dmt.md` or `[M#]` in `02-baq.md`) or displays the lab banner when a rule rests on an approved lab default."*

### `0:45 – 1:45` · 2. Running `validate_dmt.py`
- **Action**: Run the validator in the terminal:
  ```bash
  python3 dmt-validator/validate_dmt.py --data dmt-validator/sample-dirty-csvs --out proof/reports
  ```
- **Output Shown**:
  ```text
  15 errors, 0 warnings, 0 notes
  Check
  BAD_DATE                      1
  CUSTNUM_NOT_INT               2
  DUPLICATE_KEY                 2
  LOAD_ORDER                    2
  PARTPLANT_MISSING_FOR_SITE    2
  REQUIRED_MISSING              2
  UPDATE_KEY_CHANGE             2
  WHITESPACE                    2
  ```
- **Talk Track**:
  - *"In under two seconds, the script surfaces 15 blocking errors across 8 check categories and writes both a filterable CSV and a standalone HTML remediation report."*

### `1:45 – 3:30` · 3. Walking Through the HTML Remediation Report
- **Action**: Open [`proof/reports/dmt-remediation.html`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/reports/dmt-remediation.html) in the browser and highlight four representative rows:
  1. **`F014` & `F015` (`LOAD_ORDER` in `load-plan.csv`)**: `ShipTo` is scheduled before `Customer` (`[D11, D23]`, approved default 58 — *Default chosen for the lab, not confirmed against Epicor*), and `PartPlant` is scheduled before `Part` (`[D19, D20]`).
  2. **`F001` & `F007` (`CUSTNUM_NOT_INT`)**: String `CustID` values (`'LUMEN'`, `'NIMBUS'`) were pasted into the integer `CustNum` column (`[D10]`, `[M2][M3]`).
  3. **`F002` & `F010` (`UPDATE_KEY_CHANGE`)**: An `Update` row attempted to rename primary key `MFG01|BEACON` to `MFG01|BEACON-CO` (`[D21]`: Update finds the record by its primary key).
  4. **`F005` (`PARTPLANT_MISSING_FOR_SITE`)**: `OrderDtl` ships `P-1007` from `MFG02/MAIN`, where `P-1007` only has a `PartPlant` row in `MFG01` (`[D9, D19, D20]`).
  5. **`F009` & `F012` (`REQUIRED_MISSING`)**: Blank `PartDescription` (`required per cited source [D14][D15]`) and blank `PrimWhse` (`required per cited source [D9]`).

### `3:30 – 5:00` · 4. Applying Fixes & Verifying Zero Errors
- **Action**: Point `validate_dmt.py` at the remediated batch where load order is corrected (`Customer -> ShipTo -> Part -> PartPlant -> OrderHed -> OrderDtl`), whitespace is trimmed (`[D12]`), original keys are restored on `Update` rows (`[D21]`), and missing `PartPlant` setup rows are added.
- **Output Shown**:
  ```text
  0 errors, 0 warnings, 0 notes
  ```
- **Talk Track**:
  - *"Only when the batch returns `0 errors, 0 warnings` do we hand the CSVs and `load-plan.csv` (with PlayList Wait steps between parent and child loads `[D1]`) to the cutover operator."*
