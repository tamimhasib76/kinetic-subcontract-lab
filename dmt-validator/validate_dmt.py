#!/usr/bin/env python3
"""validate_dmt.py - file-only pre-load checks for a DMT batch.

Reads a folder of CSVs (Customer, ShipTo, Part, PartPlant, OrderHed, OrderDtl),
the setup reference files (reference/sites.csv, reference/uom.csv) and the run
order (load-plan.csv). Writes an HTML and a CSV remediation report.

It checks files only. It never connects to Epicor or a database, and it does not
predict what DMT does with a row that fails. Every finding carries its basis:
a source ID from docs/reference/03-dmt.md ([D#]) or 02-baq.md ([M#]), an
approved bucket A default (with the lab banner), or "lab check" where the
reference has no source.

Two ways to say Add vs Update:
- Lab mode: the file has a LabAction column (Add/Update per row) and
  LabTargetKey (key of the record an Update row targets).
- Run mode: real client files without those columns. --mode add|update sets
  the action for the whole run, as DMT does per import [D2][D1]. Key changes
  on Update rows are caught only with a before-image (--before).

Usage:
    python validate_dmt.py --data sample-dirty-csvs --out reports
    python validate_dmt.py --data client-files --mode update --before Part=part-before.csv
"""
import argparse
import html
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

BANNER = "Default chosen for the lab, not confirmed against Epicor."
LAB_COLS = ("LabAction", "LabTargetKey")
ACTIONS = ("Add", "Update")

ENTITIES = {
    "Customer": {"file": "Customer.csv", "key": ["Company", "CustID"]},
    "ShipTo": {"file": "ShipTo.csv", "key": ["Company", "CustNumCustID", "ShipToNum"]},
    "Part": {"file": "Part.csv", "key": ["Company", "PartNum"]},
    "PartPlant": {"file": "PartPlant.csv", "key": ["Company", "PartNum", "Plant"]},
    "OrderHed": {"file": "OrderHed.csv", "key": ["Company", "OrderNum"]},
    "OrderDtl": {"file": "OrderDtl.csv", "key": ["Company", "OrderNum", "OrderLine"]},
}

# Basis for the duplicate-key check: (basis text, banner?)
KEY_BASIS = {
    "Customer": ("lab check: lab key (Company, CustID); the table key is not stated in the reference", False),
    "ShipTo": ("lab check: lab key (Company, CustNumCustID, ShipToNum); the table key is not stated in the reference", False),
    "Part": ("lab check: lab key (Company, PartNum); the table key is not stated in the reference", False),
    "PartPlant": ("approved lab default 54 (Company, PartNum, Plant as keys)", True),
    "OrderHed": ("lab check: lab key (Company, OrderNum); see [D6][D7] for OrderNum = 0 and order numbering", False),
    "OrderDtl": ("cited source [D6]: rows sharing an order need distinct OrderLine values", False),
}

# Required columns: (column, cited source text, approved-default note or None).
# Only columns that 03-dmt.md section 3 shows as needed, or that an approved
# bucket A default makes required. Applied to Add and Update rows alike:
# required fields are enforced on update as well as add [D15] (03-dmt.md 2.6).
REQUIRED = {
    "ShipTo": [("CustNumCustID", "[D10][D11]", None)],
    "Part": [("PartNum", "[D14]", None), ("PartDescription", "[D14][D15]", None)],
    "PartPlant": [
        ("Company", "[D19]", "approved lab default 54"),
        ("PartNum", "[D19]", "approved lab default 54"),
        ("Plant", "[D19]", "approved lab default 54"),
        ("PrimWhse", "[D9]", None),
    ],
    "OrderHed": [
        ("Company", "[D8]", None),
        ("OrderNum", "[D8]", None),
        ("CustomerCustID", "[D8]", "approved lab default 57"),
    ],
}

# Warn-only columns (approved default 53: warn, do not fail).
WARN_IF_MISSING = {"Part": [("TypeCode", "approved lab default 53")]}

INT_COLS = {
    "OrderHed": ["OrderNum"],
    "OrderDtl": ["OrderNum", "OrderLine", "OrderRel#OrderRelNum"],
}
CUSTNUM_COLS = {"Customer": ["CustNum"], "OrderHed": ["CustNum"]}
DECIMAL_COLS = {"OrderDtl": ["SellingQuantity"]}
DATE_COLS = {"OrderHed": ["OrderDate", "RequestDate", "NeedByDate"]}
UOM_COLS = ["IUM", "PUM", "SalesUM"]

# Load-order rules: (parent, child, basis, banner?)
LOAD_RULES = [
    ("Customer", "ShipTo", "approved lab default 58; parent-first rule [D23]; CustNumCustID lookup [D11]", True),
    ("Part", "PartPlant", "cited source [D19] (Part, then PartPlant, then PartWhse); also [D20]", False),
    ("Customer", "OrderHed", "approved lab default 59; CustomerCustID lookup [D8]", True),
    ("Part", "OrderDtl", "approved lab default 59; OrderDtl#PartNum lookup [D8]", True),
]

HIDDEN = re.compile(r"[\x00-\x1f\x7f\u00a0\u200b\ufeff]")
INT_RE = re.compile(r"^-?\d+$")
DEC_RE = re.compile(r"^-?\d+(\.\d+)?$")


class Report:
    def __init__(self):
        self.rows = []

    def add(self, severity, check, file, row, entity_key, column, value, finding, basis, remediation, banner=False):
        self.rows.append({
            "Severity": severity,
            "Check": check,
            "File": file,
            "Row": row,
            "Key": entity_key,
            "Column": column,
            "Value": value,
            "Finding": finding,
            "Basis": basis,
            "Remediation": remediation,
            "Banner": BANNER if banner else "",
        })


def s(v):
    """Value with surrounding whitespace and hidden characters removed."""
    return HIDDEN.sub("", v).strip() if isinstance(v, str) else ""


def show(v):
    """Make whitespace and hidden characters visible in the report."""
    out = v.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    out = HIDDEN.sub(lambda m: "\\u%04x" % ord(m.group()), out)
    if out != out.strip(" "):
        out = "'" + out.replace(" ", "\u00b7") + "'"
    return out


def read_csv(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, skipinitialspace=False)


def key_of(row, cols):
    return tuple(s(row.get(c, "")) for c in cols)


def key_text(k):
    return "|".join(k)


def entity_for(path_text):
    """Entity named by a before-image argument: 'Part=path.csv' or a path whose name starts with the entity."""
    if "=" in path_text:
        ent, path_text = path_text.split("=", 1)
        if ent not in ENTITIES:
            raise SystemExit(f"--before: unknown entity '{ent}' (use one of {', '.join(ENTITIES)})")
        return ent, Path(path_text)
    stem = Path(path_text).stem.lower()
    for ent in sorted(ENTITIES, key=len, reverse=True):  # PartPlant before Part
        if stem.startswith(ent.lower()):
            return ent, Path(path_text)
    raise SystemExit(f"--before: cannot tell the entity of '{path_text}'; write it as Entity=path")


def load_before(items):
    """Key sets of records already in the target, per entity."""
    before = {}
    for item in items or []:
        ent, path = entity_for(item)
        if not path.exists():
            raise SystemExit(f"--before: {path} not found")
        df = read_csv(path)
        kc = ENTITIES[ent]["key"]
        missing = [c for c in kc if c not in df.columns]
        if missing:
            raise SystemExit(f"--before: {path} lacks key column(s) {', '.join(missing)} for {ent}")
        before.setdefault(ent, set()).update(key_of(r, kc) for _, r in df.iterrows())
    return before


def load(data_dir, rep, mode=None, before=None):
    frames = {}
    needs_mode = []
    for ent, meta in ENTITIES.items():
        p = data_dir / meta["file"]
        if not p.exists():
            rep.add("WARNING", "FILE_MISSING", meta["file"], "", "", "", "",
                    f"{meta['file']} not found; checks that need {ent} are skipped.",
                    "lab check", f"Add {meta['file']} or ignore if {ent} is not in this batch.")
            continue
        df = read_csv(p)
        df.index = range(2, len(df) + 2)  # row number as seen in a spreadsheet (header = row 1)
        df.attrs["lab"] = "LabAction" in df.columns
        df.attrs["before"] = (before or {}).get(ent, set())
        if df.attrs["lab"]:
            if mode:
                rep.add("INFO", "MODE_IGNORED", meta["file"], 1, "", "LabAction", "",
                        f"File has a LabAction column, so per-row actions are used and --mode {mode} is ignored for it.",
                        "lab check", "Drop LabAction/LabTargetKey to validate the file in run mode.")
        elif mode:
            df["LabAction"] = mode.capitalize()
        else:
            needs_mode.append(meta["file"])
        if "LabTargetKey" not in df.columns:
            df["LabTargetKey"] = ""
        frames[ent] = df
    if needs_mode:
        raise SystemExit("No LabAction column in " + ", ".join(needs_mode) +
                         ". Give --mode add or --mode update (DMT sets the action per import run).")
    ref = {}
    for name in ("sites", "uom"):
        p = data_dir / "reference" / f"{name}.csv"
        if p.exists():
            ref[name] = read_csv(p)
        else:
            rep.add("WARNING", "FILE_MISSING", f"reference/{name}.csv", "", "", "", "",
                    f"reference/{name}.csv not found; its checks are skipped.", "lab check",
                    f"Export the target's {name} setup to reference/{name}.csv.")
    plan_path = data_dir / "load-plan.csv"
    plan = read_csv(plan_path) if plan_path.exists() else None
    if plan is None:
        rep.add("WARNING", "FILE_MISSING", "load-plan.csv", "", "", "", "",
                "load-plan.csv not found; load order is not checked.", "lab check",
                "Add load-plan.csv (Seq, Entity, File).")
    return frames, ref, plan


def existing_keys(df, cols):
    """Keys of rows in the file, records that Update rows target, and before-image records."""
    keys = set(df.attrs.get("before", ()))
    for _, r in df.iterrows():
        keys.add(key_of(r, cols))
        if s(r["LabAction"]) == "Update" and s(r["LabTargetKey"]):
            keys.add(tuple(p.strip() for p in r["LabTargetKey"].split("|")))
    return keys


def check_load_order(plan, rep):
    if plan is None:
        return
    plan = plan.copy()
    plan.index = range(2, len(plan) + 2)
    seq = {}
    for i, r in plan.iterrows():
        ent = s(r.get("Entity", ""))
        if not INT_RE.match(s(r.get("Seq", ""))):
            rep.add("ERROR", "TYPE_INT", "load-plan.csv", i, ent, "Seq", show(r.get("Seq", "")),
                    "Seq is not an integer.", "lab check", "Number the steps 1, 2, 3 ...")
            continue
        seq[ent] = (int(s(r["Seq"])), i)
    for ent in ENTITIES:
        if ent not in seq:
            rep.add("WARNING", "LOAD_PLAN_GAP", "load-plan.csv", "", ent, "Entity", "",
                    f"{ent} is not in the load plan; its order is not checked.", "lab check",
                    f"Add {ent} to load-plan.csv or confirm it is out of this batch.")
    for parent, child, basis, banner in LOAD_RULES:
        if parent in seq and child in seq and seq[child][0] <= seq[parent][0]:
            rep.add("ERROR", "LOAD_ORDER", "load-plan.csv", seq[child][1], child, "Seq", str(seq[child][0]),
                    f"{child} (step {seq[child][0]}) is planned before or with {parent} (step {seq[parent][0]}); "
                    f"{parent} must load first per {basis}.",
                    basis, f"Move {child} after {parent} in the load plan (use a PlayList Wait between them [D1]).",
                    banner)


def check_lab_columns(ent, df, rep):
    f = ENTITIES[ent]["file"]
    kc = ENTITIES[ent]["key"]
    if not df.attrs["lab"]:
        check_run_mode_keys(ent, df, rep)
        return
    for i, r in df.iterrows():
        act = s(r["LabAction"])
        k = key_of(r, kc)
        if act not in ACTIONS:
            rep.add("ERROR", "LAB_ACTION_INVALID", f, i, key_text(k), "LabAction", show(r["LabAction"]),
                    "LabAction must be Add or Update.", "lab check", "Set LabAction to Add or Update.")
            continue
        if act != "Update":
            continue
        tgt = s(r["LabTargetKey"])
        if not tgt:
            rep.add("WARNING", "LAB_TARGET_MISSING", f, i, key_text(k), "LabTargetKey", "",
                    "Update row has no LabTargetKey, so a key change cannot be detected.", "lab check",
                    "Fill LabTargetKey with the key of the record being updated (pipe-separated).")
            continue
        parts = [p.strip() for p in r["LabTargetKey"].split("|")]
        changed = [c for c, a, b in zip(kc, k, parts) if a != b]
        if len(parts) != len(kc):
            rep.add("ERROR", "LAB_TARGET_INVALID", f, i, key_text(k), "LabTargetKey", show(tgt),
                    f"LabTargetKey must have {len(kc)} parts ({', '.join(kc)}).", "lab check",
                    "Fix LabTargetKey.")
        elif changed:
            rep.add("ERROR", "UPDATE_KEY_CHANGE", f, i, key_text(k), ", ".join(changed),
                    f"{key_text(k)} (target {tgt})",
                    f"Update row changes key column(s) {', '.join(changed)}: target record {tgt}, row key {key_text(k)}. "
                    "Per cited source [D21], Update finds the record by its primary key, so an Update row cannot carry a new key.",
                    "cited source [D21] (03-dmt.md 2.3)",
                    "Restore the original key on this row. Treat a key rename as a separate, approved step outside this load.")


def check_run_mode_keys(ent, df, rep):
    """Run mode: no LabTargetKey, so key changes need a before-image of the target records."""
    f = ENTITIES[ent]["file"]
    kc = ENTITIES[ent]["key"]
    action = s(df["LabAction"].iloc[0]) if len(df) else ""
    before = df.attrs["before"]
    if action != "Update":
        rep.add("INFO", "KEY_CHANGE_NOT_CHECKED", f, "", "", ", ".join(kc), "",
                "Run mode Add: the per-row key-change check does not apply. In update mode it needs a before-image file (--before).",
                "lab check", "None for an Add run.")
        return
    if not before:
        rep.add("INFO", "KEY_CHANGE_NOT_CHECKED", f, "", "", ", ".join(kc), "",
                "Run mode Update without a before-image: key changes on Update rows were NOT checked.",
                "cited source [D21]: Update finds the record by its primary key",
                f"Export the current {ent} records (at least {', '.join(kc)}) and pass --before {ent}=<file>.")
        return
    for i, r in df.iterrows():
        k = key_of(r, kc)
        if all(k) and k not in before:
            rep.add("ERROR", "UPDATE_KEY_CHANGE", f, i, key_text(k), ", ".join(kc), key_text(k),
                    f"Update row key {key_text(k)} is not in the before-image: either a key column was changed or the record does not exist. "
                    "Per cited source [D21], Update finds the record by its primary key.",
                    "cited source [D21] (03-dmt.md 2.3); before-image comparison",
                    "Restore the original key, or move a genuinely new record to an Add run.")


def check_required(ent, df, rep):
    f = ENTITIES[ent]["file"]
    kc = ENTITIES[ent]["key"]
    for col, src, default in REQUIRED.get(ent, []):
        basis = f"cited source {src}" + (f"; {default}" if default else "")
        wording = f"required per cited source {src}" + (f" ({default})" if default else "")
        if col not in df.columns:
            rep.add("ERROR", "REQUIRED_MISSING", f, 1, "", col, "",
                    f"Column '{col}' is missing from the file; {wording}.", basis,
                    f"Add the '{col}' column. Confirm the full list with the Template Builder / Required button on the client's DMT version [D21][D23].",
                    bool(default))
            continue
        for i, r in df.iterrows():
            if not s(r[col]):
                rep.add("ERROR", "REQUIRED_MISSING", f, i, key_text(key_of(r, kc)), col, show(r[col]),
                        f"Column '{col}' is blank on this {s(r['LabAction']) or 'Add'} row; {wording}.", basis,
                        f"Fill '{col}'.", bool(default))
    for col, default in WARN_IF_MISSING.get(ent, []):
        if col not in df.columns:
            rep.add("WARNING", "OPTIONAL_MISSING", f, 1, "", col, "",
                    f"Column '{col}' is missing; {default} warns but does not fail.", default,
                    f"Consider adding '{col}'.", True)
            continue
        for i, r in df.iterrows():
            if not s(r[col]):
                rep.add("WARNING", "OPTIONAL_MISSING", f, i, key_text(key_of(r, kc)), col, "",
                        f"'{col}' is blank; {default} warns but does not fail.", default,
                        f"Consider filling '{col}'.", True)
    # Default ShipTo cannot be updated through the ShipTo template [D24].
    if ent == "ShipTo" and "ShipToNum" in df.columns:
        for i, r in df.iterrows():
            if s(r["LabAction"]) == "Update" and not s(r["ShipToNum"]):
                rep.add("ERROR", "SHIPTO_DEFAULT_UPDATE", f, i, key_text(key_of(r, kc)), "ShipToNum", "",
                        "Update row with blank ShipToNum targets the default ShipTo; per cited source [D24] that cannot be updated through the ShipTo template.",
                        "cited source [D24]", "Update the default ShipTo through the Customer template instead [D24].")


def check_whitespace(ent, df, rep):
    f = ENTITIES[ent]["file"]
    kc = ENTITIES[ent]["key"]
    for col in df.columns:
        if col in LAB_COLS:
            continue
        for i, v in df[col].items():
            if v and (v != v.strip() or HIDDEN.search(v)):
                rep.add("ERROR", "WHITESPACE", f, i, key_text(key_of(df.loc[i], kc)), col, show(v),
                        f"'{col}' has leading/trailing whitespace or a hidden character.",
                        "cited source [D12]: hidden characters cause lookup failures (03-dmt.md 1.9)",
                        "Trim the value (Excel CLEAN/TRIM, or check in a text editor) [D12].")


def check_types(ent, df, rep, date_fmt):
    f = ENTITIES[ent]["file"]
    kc = ENTITIES[ent]["key"]
    for col in CUSTNUM_COLS.get(ent, []):
        if col not in df.columns:
            continue
        for i, v in df[col].items():
            if s(v) and not INT_RE.match(s(v)):
                rep.add("ERROR", "CUSTNUM_NOT_INT", f, i, key_text(key_of(df.loc[i], kc)), col, show(v),
                        f"CustNum holds '{s(v)}', which is not an integer. CustNum is the internal customer number; "
                        "CustID is the editable string ID [D10]. A SQL join or compare against the int column converts the "
                        "varchar side to int and fails with error 245 [M2][M3].",
                        "cited sources [D10]; [M2][M3] in 02-baq.md (fix-drill defect 2)",
                        "Move the CustID to the lookup column (CustID / CustNumCustID / CustomerCustID [D11][D8]); "
                        "put the integer CustNum here or leave it blank.")
    for col in INT_COLS.get(ent, []):
        if col not in df.columns:
            continue
        for i, v in df[col].items():
            if s(v) and not INT_RE.match(s(v)):
                rep.add("ERROR", "TYPE_INT", f, i, key_text(key_of(df.loc[i], kc)), col, show(v),
                        f"'{col}' is not an integer.", "lab check: integer key column", f"Give an integer {col}.")
    for col in DECIMAL_COLS.get(ent, []):
        if col not in df.columns:
            continue
        for i, v in df[col].items():
            if s(v) and not DEC_RE.match(s(v)):
                rep.add("ERROR", "TYPE_DECIMAL", f, i, key_text(key_of(df.loc[i], kc)), col, show(v),
                        f"'{col}' is not a number.", "lab check", f"Give a plain number in {col} (no units or commas).")
    for col in DATE_COLS.get(ent, []):
        if col not in df.columns:
            continue
        for i, v in df[col].items():
            if not s(v):
                continue
            try:
                datetime.strptime(s(v), date_fmt)
            except ValueError:
                rep.add("ERROR", "BAD_DATE", f, i, key_text(key_of(df.loc[i], kc)), col, show(v),
                        f"'{col}' does not match the batch date format {date_fmt}.",
                        "lab check: the reference cites no DMT date format (UNVERIFIED); the batch format is set with --date-format",
                        "Re-enter the date in the batch format. Do not guess day/month order on ambiguous values; check the legacy record.")


def check_duplicates(ent, df, rep):
    f = ENTITIES[ent]["file"]
    kc = ENTITIES[ent]["key"]
    if not all(c in df.columns for c in kc):
        return
    basis, banner = KEY_BASIS[ent]
    seen = {}
    for i, r in df.iterrows():
        k = key_of(r, kc)
        if not all(k):
            continue
        if k in seen:
            rep.add("ERROR", "DUPLICATE_KEY", f, i, key_text(k), ", ".join(kc), key_text(k),
                    f"Duplicate key {key_text(k)}; first seen on row {seen[k]}.", basis,
                    "Keep one row per key; merge or renumber the other.", banner)
        else:
            seen[k] = i


def fk(rep, ent, df, cols, parent_keys, parent, check, basis, banner, remediation):
    f = ENTITIES[ent]["file"]
    kc = ENTITIES[ent]["key"]
    if not all(c in df.columns for c in cols):
        return
    for i, r in df.iterrows():
        k = key_of(r, cols)
        if not all(k):
            continue
        if k not in parent_keys:
            rep.add("ERROR", check, f, i, key_text(key_of(r, kc)), ", ".join(cols), key_text(k),
                    f"{key_text(k)} has no matching {parent} row in this batch (or record targeted by an Update row).",
                    basis, remediation, banner)


def check_cross_file(frames, ref, rep):
    cust, ship, part, pp, oh, od = (frames.get(e) for e in ENTITIES)
    sites = ref.get("sites")
    uom = ref.get("uom")
    site_keys = {(s(r["Company"]), s(r["Plant"])) for _, r in sites.iterrows()} if sites is not None else None
    whse_keys = {(s(r["Company"]), s(r["Plant"]), s(r["WarehouseCode"])) for _, r in sites.iterrows()} if sites is not None else None
    uom_keys = {(s(r["Company"]), s(r["UOMCode"])) for _, r in uom.iterrows()} if uom is not None else None

    if cust is not None:
        ck = existing_keys(cust, ["Company", "CustID"])
        if ship is not None:
            fk(rep, "ShipTo", ship, ["Company", "CustNumCustID"], ck, "Customer", "FK_CUSTOMER",
               "approved lab default 58; CustNumCustID lookup [D11]", True,
               "Load the customer first, or correct CustNumCustID to an existing CustID in the same Company.")
        if oh is not None:
            fk(rep, "OrderHed", oh, ["Company", "CustomerCustID"], ck, "Customer", "FK_CUSTOMER",
               "approved lab default 59; CustomerCustID lookup [D8]", True,
               "Load the customer first, or correct CustomerCustID to an existing CustID in the same Company.")
            # CustNum given on the order must match the customer's CustNum in the same Company.
            cnum = {key_of(r, ["Company", "CustID"]): s(r["CustNum"]) for _, r in cust.iterrows()
                    if "CustNum" in cust.columns and INT_RE.match(s(r["CustNum"]))}
            if "CustNum" in oh.columns:
                for i, r in oh.iterrows():
                    v = s(r["CustNum"])
                    k = key_of(r, ["Company", "CustomerCustID"])
                    if INT_RE.match(v) and k in cnum and cnum[k] != v:
                        rep.add("ERROR", "CUSTNUM_MISMATCH", "OrderHed.csv", i, key_text(key_of(r, ["Company", "OrderNum"])),
                                "CustNum", v,
                                f"CustNum {v} does not match Customer {key_text(k)} (CustNum {cnum[k]}). The same CustID can carry a different CustNum in each Company.",
                                "lab check; CustNum vs CustID [D10]", "Leave CustNum blank and let CustomerCustID resolve it [D8], or correct it.")
    if part is not None:
        pk = existing_keys(part, ["Company", "PartNum"])
        if pp is not None:
            fk(rep, "PartPlant", pp, ["Company", "PartNum"], pk, "Part", "FK_PART",
               "cited source [D19] (Part before PartPlant)", False, "Load the part first, or correct PartNum.")
        if od is not None:
            fk(rep, "OrderDtl", od, ["Company", "PartNum"], pk, "Part", "FK_PART",
               "approved lab default 59; OrderDtl#PartNum lookup [D8]", True, "Load the part first, or correct PartNum.")
        if uom_keys is not None:
            for col in UOM_COLS:
                if col not in part.columns:
                    continue
                for i, r in part.iterrows():
                    v = s(r[col])
                    if v and (s(r["Company"]), v) not in uom_keys:
                        rep.add("ERROR", "UOM_NOT_FOUND", "Part.csv", i, key_text(key_of(r, ["Company", "PartNum"])), col, show(r[col]),
                                f"UOM '{v}' is not in reference/uom.csv for {s(r['Company'])}.",
                                "cited source [D13]: UOM classes/conversions must exist before Part; codes must exist in the class",
                                "Use the exact UOM code from the target's UOM class, or set the UOM up first [D13].")
    if oh is not None and od is not None:
        fk(rep, "OrderDtl", od, ["Company", "OrderNum"], existing_keys(oh, ["Company", "OrderNum"]), "OrderHed",
           "FK_ORDERHED", "lab check: line needs its order header", False, "Add the order header or correct OrderNum.")

    if pp is not None and site_keys is not None:
        for i, r in pp.iterrows():
            k = key_text(key_of(r, ["Company", "PartNum", "Plant"]))
            co, pl, wh = s(r["Company"]), s(r.get("Plant", "")), s(r.get("PrimWhse", ""))
            if pl and (co, pl) not in site_keys:
                case = any(c == co and p.lower() == pl.lower() for c, p in site_keys)
                rep.add("ERROR", "SITE_UNKNOWN", "PartPlant.csv", i, k, "Plant", show(r["Plant"]),
                        f"Plant '{pl}' is not a site of {co} in reference/sites.csv" + (" (matches only if case is ignored)." if case else "."),
                        "cited sources [D19]; [D14] plant/warehouse IDs may be case-sensitive",
                        "Map the legacy site to the target Plant code exactly.")
            elif pl and wh and (co, pl, wh) not in whse_keys:
                rep.add("ERROR", "WHSE_NOT_IN_SITE", "PartPlant.csv", i, k, "PrimWhse", show(r["PrimWhse"]),
                        f"PrimWhse '{wh}' is not a warehouse of {co}/{pl} in reference/sites.csv.",
                        "cited source [D9]: the warehouse must be set up and valid in the site",
                        "Use a warehouse of that site, or set it up first [D9].")

    if od is not None and "OrderRel#Plant" in od.columns:
        pp_keys = existing_keys(pp, ["Company", "PartNum", "Plant"]) if pp is not None else None
        part_keys = existing_keys(part, ["Company", "PartNum"]) if part is not None else None
        for i, r in od.iterrows():
            co, pn, pl = s(r["Company"]), s(r.get("PartNum", "")), s(r["OrderRel#Plant"])
            k = key_text(key_of(r, ["Company", "OrderNum", "OrderLine"]))
            if not pl:
                continue
            if site_keys is not None and (co, pl) not in site_keys:
                rep.add("ERROR", "SITE_UNKNOWN", "OrderDtl.csv", i, k, "OrderRel#Plant", show(r["OrderRel#Plant"]),
                        f"Plant '{pl}' is not a site of {co} in reference/sites.csv.",
                        "lab check: site mapping; [D14] plant IDs may be case-sensitive",
                        "Map the legacy ship site to the target Plant code exactly.")
                continue
            if pp_keys is None or not pn or (part_keys is not None and (co, pn) not in part_keys):
                continue
            if (co, pn, pl) not in pp_keys:
                other = sorted(c for c, p, s_ in pp_keys if p == pn and s_ == pl and c != co)
                note = f" A PartPlant row for {pn}/{pl} exists in {', '.join(other)} only; rows do not carry across companies." if other else ""
                rep.add("ERROR", "PARTPLANT_MISSING_FOR_SITE", "OrderDtl.csv", i, k, "PartNum, OrderRel#Plant", f"{pn} @ {pl}",
                        f"Part {pn} has no PartPlant row for {co}/{pl}, the site this line ships from.{note}",
                        "lab check: PartPlant holds per-site part data (PrimWhse per site [D9]; Part then PartPlant [D19][D20]). "
                        "No cited source states what happens to such a line; this is reported as a data gap",
                        "Add the PartPlant row for this Company and site (with a PrimWhse valid in that site), or ship from a site the part is set up in.")


CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--muted:#5f6368;--line:#d9dce1;--err:#b3261e;--warn:#8a5a00;--chip:#f1f3f4}
@media (prefers-color-scheme:dark){:root{--bg:#16181b;--fg:#e8eaed;--muted:#9aa0a6;--line:#3c4043;--err:#f28b82;--warn:#fdd663;--chip:#26292d}}
body{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}
main{max-width:1200px;margin:0 auto}h1{font-size:22px;margin:0 0 4px}p.meta{color:var(--muted);margin:0 0 16px}
table{border-collapse:collapse;width:100%;margin:8px 0 24px}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{font-weight:600;position:sticky;top:0;background:var(--bg)}td.v{font-family:ui-monospace,monospace;white-space:pre-wrap}
.ERROR{color:var(--err);font-weight:600}.INFO{color:var(--muted);font-weight:600}.WARNING{color:var(--warn);font-weight:600}.banner{background:var(--chip);padding:2px 6px;border-radius:4px;font-size:12px}
.scroll{overflow-x:auto}.note{background:var(--chip);padding:12px 16px;border-radius:6px}
"""


def write_reports(rep, out_dir, data_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rep.rows, columns=["Severity", "Check", "File", "Row", "Key", "Column", "Value",
                                         "Finding", "Basis", "Remediation", "Banner"])
    if not df.empty:
        df["_sev"] = df["Severity"].map({"ERROR": 0, "WARNING": 1, "INFO": 2})
        df["_row"] = pd.to_numeric(df["Row"], errors="coerce").fillna(0)
        df = df.sort_values(["_sev", "File", "_row", "Check"]).drop(columns=["_sev", "_row"])
    df.insert(0, "FindingID", [f"F{n:03d}" for n in range(1, len(df) + 1)])
    df.to_csv(out_dir / "dmt-remediation.csv", index=False)

    e = lambda x: html.escape(str(x))
    summary = df.groupby(["Severity", "Check"]).size().reset_index(name="Count") if not df.empty else df
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>DMT Remediation Report</title><style>{CSS}</style></head><body><main>",
             "<h1>DMT pre-load remediation report</h1>",
             f"<p class='meta'>Source folder: {e(data_dir)} &middot; generated {datetime.now():%Y-%m-%d %H:%M} &middot; "
             f"{(df['Severity'] == 'ERROR').sum()} errors, {(df['Severity'] == 'WARNING').sum()} warnings, {(df['Severity'] == 'INFO').sum()} notes</p>",
             "<div class='note'><b>What this report does and does not say.</b> It checks the files only. It does not say what DMT "
             "will do with any row. [D#] and [M#] are source IDs in docs/reference/03-dmt.md and 02-baq.md. Rows marked "
             f"<span class='banner'>{e(BANNER)}</span> rest on an approved lab default. \"lab check\" means the reference has no "
             "source for the rule; it is a data-hygiene check chosen for this kit. Required-column lists come only from cited "
             "sources; confirm the full list with the Template Builder / Required button on the client's DMT version.</div>",
             "<h2>Summary</h2><table><tr><th>Severity</th><th>Check</th><th>Count</th></tr>"]
    for _, r in summary.iterrows():
        parts.append(f"<tr><td class='{e(r['Severity'])}'>{e(r['Severity'])}</td><td>{e(r['Check'])}</td><td>{r['Count']}</td></tr>")
    parts.append("</table><h2>Findings</h2><div class='scroll'><table><tr><th>ID</th><th>Severity</th><th>Check</th><th>File</th>"
                 "<th>Row</th><th>Key</th><th>Column</th><th>Value</th><th>Finding</th><th>Basis</th><th>Remediation</th></tr>")
    for _, r in df.iterrows():
        banner = f"<br><span class='banner'>{e(r['Banner'])}</span>" if r["Banner"] else ""
        parts.append(f"<tr><td>{e(r['FindingID'])}</td><td class='{e(r['Severity'])}'>{e(r['Severity'])}</td><td>{e(r['Check'])}</td>"
                     f"<td>{e(r['File'])}</td><td>{e(r['Row'])}</td><td>{e(r['Key'])}</td><td>{e(r['Column'])}</td>"
                     f"<td class='v'>{e(r['Value'])}</td><td>{e(r['Finding'])}</td><td>{e(r['Basis'])}{banner}</td><td>{e(r['Remediation'])}</td></tr>")
    parts.append("</table></div></main></body></html>")
    (out_dir / "dmt-remediation.html").write_text("\n".join(parts), encoding="utf-8")
    return df


def main(argv=None):
    ap = argparse.ArgumentParser(description="File-only DMT pre-load validator (no database, no Epicor connection).")
    ap.add_argument("--data", default="sample-dirty-csvs", help="folder with the CSVs, reference/ and load-plan.csv")
    ap.add_argument("--out", default="reports", help="output folder for dmt-remediation.html/.csv")
    ap.add_argument("--date-format", default="%Y-%m-%d", help="strptime format every date must match (default %%Y-%%m-%%d)")
    ap.add_argument("--mode", choices=["add", "update"],
                    help="action for the whole run, as DMT sets it per import; required for files without a LabAction column")
    ap.add_argument("--before", action="append", metavar="[ENTITY=]FILE",
                    help="before-image of records already in the target (repeatable). In update mode, Update keys are "
                         "compared against it to catch key changes; in any mode its keys count as existing parents")
    args = ap.parse_args(argv)

    data_dir = Path(args.data)
    rep = Report()
    frames, ref, plan = load(data_dir, rep, args.mode, load_before(args.before))
    check_load_order(plan, rep)
    for ent, df in frames.items():
        check_lab_columns(ent, df, rep)
        check_required(ent, df, rep)
        check_whitespace(ent, df, rep)
        check_types(ent, df, rep, args.date_format)
        check_duplicates(ent, df, rep)
    check_cross_file(frames, ref, rep)
    df = write_reports(rep, Path(args.out), data_dir)

    errors = int((df["Severity"] == "ERROR").sum()) if not df.empty else 0
    warnings = int((df["Severity"] == "WARNING").sum()) if not df.empty else 0
    notes = int((df["Severity"] == "INFO").sum()) if not df.empty else 0
    print(f"{errors} errors, {warnings} warnings, {notes} notes")
    if not df.empty:
        print(df[df["Severity"] == "ERROR"].groupby("Check").size().to_string())
    print(f"Reports: {Path(args.out) / 'dmt-remediation.html'}, {Path(args.out) / 'dmt-remediation.csv'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
