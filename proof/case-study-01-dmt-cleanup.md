# Case Study 01: DMT Pre-Load Batch Audit & Remediation (One-Page Summary)

> **Notice**: Lab exercise on synthetic data. Not client work.
>
> **Synthetic Lab Disclosure**: All data below (`MFG01`, `MFG02`, `ORCHID`, `LUMEN`, `P-1008`, `50001`) comes from the synthetic training kit in [`dmt-validator/sample-dirty-csvs/`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/dmt-validator/sample-dirty-csvs). No SQL Server or Epicor instance ran here; [`dmt-validator/validate_dmt.py`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/dmt-validator/validate_dmt.py) is a file-only pre-load validator.
> **Lab Banner**: *"Default chosen for the lab, not confirmed against Epicor."* applies to findings resting on approved Bucket A defaults (defaults 53, 54, 57, 58, 59 in [`docs/reference/decisions.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/docs/reference/decisions.md)).

---

## 1. Problem Statement
A 6-entity DMT migration batch (`Customer.csv`, `ShipTo.csv`, `Part.csv`, `PartPlant.csv`, `OrderHed.csv`, `OrderDtl.csv`) plus `load-plan.csv` contains planted data-hygiene defects, dependency ordering inversions, primary-key mutations on `Update` rows, and cross-file foreign-key gaps. Every finding must cite its source in [`docs/reference/03-dmt.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/docs/reference/03-dmt.md) (`[D#]`) or [`docs/reference/02-baq.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/docs/reference/02-baq.md) (`[M#]`), and missing-column findings state `"required per cited source [D#]"`.

---

## 2. Validator CLI Output (Before Remediation)

Command executed locally in this session:
```bash
python3 dmt-validator/validate_dmt.py --data dmt-validator/sample-dirty-csvs --out proof/reports
```

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
Reports: proof/reports/dmt-remediation.html, proof/reports/dmt-remediation.csv
```

---

## 3. HTML & CSV Remediation Report Output (`F001`–`F015`)

Full rendered HTML report: **[`proof/reports/dmt-remediation.html`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/reports/dmt-remediation.html)** ([CSV](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/reports/dmt-remediation.csv))

| ID | Check | File (Row) | Key / Column | Value | Finding & Cited Basis |
|---|---|---|---|---|---|
| `F001` | `CUSTNUM_NOT_INT` | `Customer.csv` (40) | `MFG01\|LUMEN` (`CustNum`) | `LUMEN` | `CustNum` holds `'LUMEN'`, which is not an integer (`[D10]`; `[M2][M3]`). |
| `F002` | `UPDATE_KEY_CHANGE` | `Customer.csv` (43) | `MFG01\|BEACON-CO` (`CustID`) | `MFG01\|BEACON-CO` | Update row changes primary key from `MFG01\|BEACON`; Update finds record by primary key (`[D21]`). |
| `F003` | `DUPLICATE_KEY` | `Customer.csv` (52) | `MFG02\|EMBER` (`Company, CustID`) | `MFG02\|EMBER` | Duplicate key `MFG02\|EMBER`; first seen on row 47 (lab check). |
| `F004` | `DUPLICATE_KEY` | `OrderDtl.csv` (4) | `MFG01\|50001\|2` (`Company, OrderNum, OrderLine`) | `MFG01\|50001\|2` | Duplicate line key; rows sharing an order need distinct `OrderLine` values (`[D6]`). |
| `F005` | `PARTPLANT_MISSING_FOR_SITE` | `OrderDtl.csv` (85) | `MFG02\|70011\|1` (`PartNum, OrderRel#Plant`) | `P-1007 @MAIN` | `P-1007` has no `PartPlant` row for `MFG02/MAIN` (`[D9, D19, D20]`; `MFG01` row does not carry across companies). |
| `F006` | `PARTPLANT_MISSING_FOR_SITE` | `OrderDtl.csv` (99) | `MFG02\|70022\|1` (`PartNum, OrderRel#Plant`) | `P-1064 @EAST` | `P-1064` has no `PartPlant` row for `MFG02/EAST` (`[D9, D19, D20]`). |
| `F007` | `CUSTNUM_NOT_INT` | `OrderHed.csv` (36) | `MFG01\|50026` (`CustNum`) | `NIMBUS` | `CustNum` holds `'NIMBUS'`, which is not an integer (`[D10]`; `[M2][M3]`). |
| `F008` | `BAD_DATE` | `OrderHed.csv` (70) | `MFG02\|70019` (`RequestDate`) | `07/14/2026` | `'RequestDate'` does not match batch date format `%Y-%m-%d` (lab check). |
| `F009` | `REQUIRED_MISSING` | `Part.csv` (20) | `MFG02\|P-1008` (`PartDescription`) | *(blank)* | Column `'PartDescription'` is blank on this Add row; required per cited source `[D14][D15]`. |
| `F010` | `UPDATE_KEY_CHANGE` | `Part.csv` (27) | `MFG01\|P-1009A` (`PartNum`) | `MFG01\|P-1009A` | Update row changes key column `PartNum` from `MFG01\|P-1009` (`[D21]`). |
| `F011` | `WHITESPACE` | `Part.csv` (48) | `MFG01\|P-1019` (`PartNum`) | `'P-1019·'` | `'PartNum'` has trailing whitespace (`[D12]`). |
| `F012` | `REQUIRED_MISSING` | `PartPlant.csv` (52) | `MFG01\|P-1014\|MAIN` (`PrimWhse`) | *(blank)* | Column `'PrimWhse'` is blank on this Add row; required per cited source `[D9]`. |
| `F013` | `WHITESPACE` | `ShipTo.csv` (61) | `MFG02\|HARBOR\|01` (`CustNumCustID`) | `'·HARBOR'` | `'CustNumCustID'` has leading whitespace (`[D12]`). |
| `F014` | `LOAD_ORDER` | `load-plan.csv` (2) | `ShipTo` (`Seq`) | `1` | `ShipTo` (step 1) is planned before `Customer` (step 2); `Customer` must load first per approved lab default 58; `[D23, D11]` (*Default chosen for the lab, not confirmed against Epicor*). |
| `F015` | `LOAD_ORDER` | `load-plan.csv` (4) | `PartPlant` (`Seq`) | `3` | `PartPlant` (step 3) is planned before `Part` (step 4); `Part` must load first per cited source `[D19]` (`[D20]`). |

---

## 4. Validator CLI Output (After Remediation)
```text
0 errors, 0 warnings, 0 notes
```
