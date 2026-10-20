# Triage Playbook: One-Week Read-Only Report Audit (paid, fixed fee)

A five-day, fixed-fee audit of a client's report backlog before a Kinetic cloud
cutover. It ends with a filled `report-inventory-template.csv`, a decision per report
(`decision-matrix.md`), and a fixed-scope quote for the follow-on work.

**Read-only means read-only.** During the audit you change nothing in the client's
system: no RDD saves, no style uploads, no BAQ saves, no DMT runs, no SQL writes. If a
fix is obvious, write it into the quote; do not apply it.

References: `docs/reference/04-cloud-rules.md` (cloud rules, cited as **04 §x**),
`02-baq.md` (BAQ defects), `01-ssrs-forms.md` (report styles and RDDs),
`needs-confirmation.md` (standing first-ticket questions a–e).

---

## Before day 1: contract and access (unbilled)

1. **Statement of work.** Fixed fee, five working days, read-only, deliverables
   listed below. Anything outside the inventory (fixes, DMT loads, new reports) is a
   separate quote.
2. **Access request.** Ask for, in writing:
   - a Kinetic user that can open Report Style, Report Data Definition and BAQ
     Designer, and run BAQs. Ask the client's admin to keep it read-only where
     their security allows;
   - on-prem only: read access to the SSRS report server folder list and the
     subscriptions list. If a Crystal or direct-SQL inventory needs SQL access, ask
     for a read-only login on a **copy**, never production;
   - a named client contact for each report owner group.
3. **Standing questions** (needs-confirmation.md a–e). Send them before day 1:
   - a. Report Builder version matching their SSRS server.
   - b. Whether Publish saves to the report style on their release.
   - c. Base dataset query in the downloaded RDL (collected on day 2).
   - d. Release and deployment: on-prem, public cloud or private cloud, plus the exact build.
   - e. Which RDD each form's base style uses (e.g. AR_Form: ARInvoice or ARForm).

## Day 1: collect the list

1. Export the report style list, the BAQ list and the BAQ Report list from Kinetic.
   On-prem, also export the SSRS folder listing and subscriptions.
2. Ask each owner group for "reports we run outside Epicor": Crystal files, Excel
   with ODBC, Power BI, SQL Agent jobs. These are the items most likely to be blocked
   on cloud (04 §1.1, §1.2).
3. Put one row per report into `report-inventory-template.csv`. Keep the client's
   wording in **Notes (as found)**; do not clean it up yet.
4. Fill **Owner**, **Last Run**, **Runs (90d)** from the system where possible.
   Leave a cell blank rather than guess.

Output: raw inventory, usually 20–60 rows.

## Day 2: classify data access

For each row, record **Current Type** and **Data Access**:

| Found | Data Access value | Gate (decision-matrix.md) |
|-------|-------------------|---------------------------|
| Report style on a standard RDD | RDD + RDL (TableGuid) | none |
| BAQ / BAQ Report | BAQ | none |
| SSRS report with its own SQL data source | SSRS shared data source -> ERP DB | G3 |
| Stored-procedure dataset | Stored procedure | G4 |
| SQL view in the ERP DB | Direct SQL view | G5 |
| Crystal or Excel over ODBC | ODBC direct to ERP SQL | G3 |
| BPM/Function writing files | System.IO to <path> | G6 |

How to check without changing anything:
- **Report styles:** download the style's RDL (on cloud, the zip) and read the
  dataset query and data source. Note whether the query uses
  `Parameters!TableGuid.Value` (RDD pattern, 04 §2.1) or a connection string (G3).
  Record the RDL namespace; a 2016 re-save failed on cloud once (04 §1.21).
- **RDDs:** open, read and close. Do not save.
- **BAQs:** open in the designer and read the relations and calculated fields. Do
  not save. Test runs are allowed.

## Day 3: measure and look for defects

1. For each slow BAQ, run **Get Query Execution Plan** and keep the `.sqlplan`
   (04 §2.12). Note the runtime. If the designer's test run stops at 10,000 rows, say
   so in Notes.
2. Read every BAQ for the six fix-drill defects (02-baq.md): missing Company join;
   CustID joined to CustNum; OrderRel join multiplying rows; criteria on the wrong
   subquery; wrong date field per the ticket; integer division. Write the defect
   number into Notes.
3. On multi-company clients, run one BAQ per company and compare totals with the
   client's known figures. Bleed between companies shows up here.

## Day 4: decide and estimate

1. Apply `decision-matrix.md` to every row: gates first, then the target.
2. Fill **Risk**, **Cloud-Readiness**, **Target Architecture**, **Cloud Rule Refs**.
3. Fill **Fixed-Scope Estimate** in hours, using the ranges in the matrix. Add time
   for each defect flag. If a row has an open "Needs check" (e.g. standing question e),
   price it, but list the dependency.
4. Review the Retire list with each owner. Retire needs a named owner's yes; record
   who said yes and when.

## Day 5: report back

Deliverables:
1. Filled `report-inventory-template.csv`.
2. A one-page summary: counts by Target Architecture and Cloud-Readiness, the top 5
   risks, and blocked items with their 04 citation.
3. A fixed-scope quote. Group rows into work packages (standard-form mods, BAQ
   rebuilds, grid replacements, retirements) with hours per row.
4. The open-questions list: unanswered standing questions a–e plus any "Needs check" rows.
5. The `.sqlplan` files and RDL downloads collected, returned to the client.

Walk the client through it in a one-hour call. Do not start any fix until a separate
order is signed.

---

## What this playbook does not claim

- That a "Blocked" item cannot be made to run. One forum poster says direct SSRS SQL
  works in a hosted environment, unsupported (04 §1.2, CONFLICTING). The lab rule is
  to treat it as blocked.
- Exact Kinetic screen names or menu paths. Those are bucket B items to confirm on the
  first job.
- Anything about Crystal on Kinetic, report scheduling, or e-mail delivery. The
  reference has no sources on these.
