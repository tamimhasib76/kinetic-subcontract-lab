# Report cutover kit

A file-only kit for triaging a client's report backlog before a move to Kinetic
multi-tenant cloud, and for mapping SyteLine order, part and customer data to Kinetic
DMT files. No database, no scripts to run.

Source of truth: `docs/reference/04-cloud-rules.md` (cloud rules), `02-baq.md` (BAQ
defects), `03-dmt.md` (DMT columns), `decisions.md` and the approved bucket A defaults
in `needs-confirmation.md`.

## Contents

| File | Use it to |
|------|-----------|
| `report-inventory-template.csv` | List every report. 25 example rows show realistic, messy findings: standard SSRS form mods, slow BAQs, Crystal leftovers, direct-SQL reports. Replace the example rows with the client's. |
| `decision-matrix.md` | Put each report into **Keep / Rebuild as BAQ Report / Replace with Grid / Retire**. Hard gates first, then the target. Every cloud rule is cited to a 04 section. |
| `triage-playbook.md` | Run a paid, fixed-fee, one-week, read-only audit, day by day, ending in a filled inventory and a fixed-scope quote. |
| `syteline-kinetic-bridge.md` | Map `co_mst`/`coitem_mst` to OrderHed/OrderDtl/OrderRel, `item_mst` to Part/PartPlant/PartWhse, `custaddr_mst` to Customer/ShipTo. Covers the Company join rule and the CustNum (int) vs CustID (string) trap. |

## How to use it

1. Send the client the standing questions a–e (`needs-confirmation.md`) before day 1.
2. Follow `triage-playbook.md`. Fill one inventory row per report.
3. Apply `decision-matrix.md` to each row. Fill Risk, Cloud-Readiness, Target
   Architecture, Fixed-Scope Estimate and Cloud Rule Refs.
4. For data migration from SyteLine, use `syteline-kinetic-bridge.md` to build the
   extracts, then check the files with `../dmt-validator/validate_dmt.py`.

Inventory column values:
- **Risk:** High / Medium / Low.
- **Cloud-Readiness:** Ready / Needs check / Needs change / Blocked, with a short reason.
- **Target Architecture:** Keep / Rebuild as BAQ Report / Replace with Grid / Retire.
- **Fixed-Scope Estimate:** hours for the follow-on fix, from the ranges in the matrix.
- **Cloud Rule Refs:** `04: <section>`; plus `02 defect <n>` when a BAQ defect applies.

## What it does not claim

- **Cloud rules are forum-sourced.** No Epicor cloud policy document was reachable
  (04, "How to read this file"). "Blocked" means "treat as blocked" under the lab
  rules (04 §3), not "Epicor guarantees it fails". Direct SSRS SQL is CONFLICTING (04 §1.2).
- **SyteLine names are UNVERIFIED.** The reference has no SyteLine source. Confirm
  every SyteLine table and column on the client's database.
- **No Crystal, scheduling or e-mail delivery rules.** The reference has no source on
  them. The inventory classes Crystal items only by how they reach data.
- **Estimates are examples.** The hours in the template are illustrative rows, not
  a rate card.
- **Exact Kinetic screens and menu paths** are bucket B items, to confirm on the first job.
- No Epicor screenshots, logos or copied help text. All report names, owners and
  figures are fictional.
