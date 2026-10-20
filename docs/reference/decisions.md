# Decisions

Project decisions and amendments. Each entry gives the date and what it changes.

## 2026-10-20 — Phase 2b fix-drill defects (answer to P1)

The six BAQ fix-drill defects are listed in `02-baq.md`, "Phase 2b fix-drill defects":
1. Missing Company join causing multi-company bleed.
2. CustID joined to CustNum: implicit int/varchar conversion causing a
   non-numeric error, silent wrong matches, or a slow scan.
3. Release join (OrderRel) multiplying rows.
4. Criteria placed on the wrong subquery.
5. Wrong date field (OrderDate used instead of NeedByDate).
6. Integer division truncation (cast an operand to DECIMAL).

## 2026-10-20 — ARInvoice vs ARForm

Which release first switched the base AR_Form style to ARInvoice stays
CONFLICTING (`01-ssrs-forms.md`, S18 vs S35). The lab rule is standing question
(e) in `needs-confirmation.md`: always check which RDD the client's base style uses.

## 2026-10-20 — Phase 3 gate (amendment)

"Phase 3 gate: Phase 3 may start once the PackSlip/OrderAck dataset PATTERN is
confirmed (ShipHead -> ShipDtl -> RptLabels, Parameters!TableGuid.Value,
<LinkKey>_<Field> naming). Exact base queries are illustrative and carry a banner;
on real jobs, always start from the client's downloaded RDL."

Evidence for the pattern, all in `01-ssrs-forms.md` (CONFIRMED, forum):
- ShipHead → ShipDtl → RptLabels joins with `Parameters!TableGuid.Value`: S19 (2023-12-06). This came from a customized PackSlip query.
- `<LinkKey>_<Field>` naming: S16 (2024-04-05), S12 (2023-01-18).
- OrderAck: OrderHed aliased `T1` (S33); a dataset named `OrderHed` (S24).

Open items: the exact base queries are needs-confirmation questions 26–28
(bucket B). They do not block Phase 3.

## 2026-10-20 — Bucket A defaults approved

All 28 bucket A defaults in `needs-confirmation.md` are approved as written, on
one condition:

> Every A default that describes Epicor behavior (not lab design) must show a
> banner in the mock: **"Default chosen for the lab, not confirmed against Epicor."**

- **Banner required (25):** P2, 7, 9, 14, 15, 16, 18, 20, 25, 35, 38, 39, 46, 49, 53, 54, 55, 57, 58, 59, 60, 69, 70, 71, 75.
  - The project owner named **item 7** (Definition = inner join, Output = left outer join) specifically.
  - Item 9 is classed as Epicor behavior, to be conservative: "no column limit" implies something about Epicor.
- **No banner, lab design only (3):**
  - 19: mock UD naming.
  - 22: mock RDL authoring namespace. It keeps its own banner: cloud may reject 2016/01.
  - 37: labs avoid referencing one calculated field from another.

The banner column for each item is in the bucket A table of `needs-confirmation.md`.
Bucket B items keep their first-job warning banner. Bucket C stays parked.

## 2026-10-20 — Fix-drill citation fixes (02-baq.md)

- **Defect 2** (CustID joined to CustNum) is CONFIRMED by Microsoft Learn:
  - "Data Type Precedence (Transact-SQL)": int outranks varchar, so the varchar side is converted to int.
  - "Database Engine events and errors (0 to 999)": error 245, "Conversion failed when converting the %ls value '%.*ls' to data type %ls."
- **Defect 5** (wrong date field) is defined by ticket spec, not an Epicor rule. The drill's ticket text states which date the report must use. The UNVERIFIED label is removed.
