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
