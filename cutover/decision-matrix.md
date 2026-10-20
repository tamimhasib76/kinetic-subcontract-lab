# Report Decision Matrix: Keep / Rebuild as BAQ Report / Replace with Grid / Retire

Use this matrix to put every row of `report-inventory-template.csv` into one of four
target architectures. Cloud rules are cited by section number from
`docs/reference/04-cloud-rules.md` (e.g. **04 §1.2**). Lab rules are in 04 §3.
BAQ defects are from `02-baq.md`, "Phase 2b fix-drill defects".

**Evidence level.** Every CONFIRMED item in 04 rests on forum posts. No Epicor cloud
policy document was reachable (04, "How to read this file"). Treat the matrix as a
triage tool, not as an Epicor statement. Where a rule rests on an approved bucket A
default, it carries the banner: **"Default chosen for the lab, not confirmed against
Epicor."**

## Step 1: hard gates (apply in order; the first match decides)

| # | If the report... | Then | Cloud basis |
|---|------------------|------|-------------|
| G1 | has had no runs in the review window AND no owner will sponsor it | **Retire** | none needed (business decision) |
| G2 | duplicates another report (same data, same audience) | **Retire** the copy, keep the better one | none needed |
| G3 | reads the ERP database through its own SQL data source (SSRS shared data source, Crystal ODBC, Excel ODBC) | **Not Keep**. Go to step 2 and choose Rebuild, Grid or Retire | 04 §1.1 (no direct SQL in cloud); §1.2 ("not a supported Epicor configuration"; CONFLICTING, lab rule: blocked; default 69, banner) |
| G4 | uses a stored-procedure dataset | **Not Keep** | 04 §1.17 (UNVERIFIED as a stated rule; approved default 75, banner); §1.15–1.16 |
| G5 | depends on SQL views in the ERP database | **Not Keep** | 04 §1.5 (UNVERIFIED; approved default 70: not allowed, banner) |
| G6 | writes files with `System.IO` to an arbitrary path | **Not Keep as is**. Rework the file output (Sandbox folders + Server File Download) | 04 §1.7, §1.8, §2.8; lab rule 4 |
| G7 | must print from MES | Stay on a **standard RDD + RDL** (Keep). A BAQ-based RDD cannot be added to MES | 04 §2.4 |

## Step 2: choose the target

| Target | Choose it when | Cloud-safe path | Cloud basis | Typical fixed scope |
|--------|----------------|-----------------|-------------|---------------------|
| **Keep** | It is a standard form (PackSlip, OrderAck, AR invoice, PO, job traveler, labels), or a BAQ Report that works, and it passes every gate in step 1. Includes "keep, but fix the defect" (e.g. an integer-division calc field). | Modify the standard RDD + RDL: duplicate the RDD, un-exclude columns, add linked tables, edit the dataset query with `Parameters!TableGuid.Value`. Start from a copy of the out-of-box style and use the names in the downloaded zip. After every upload or Publish, re-download and verify. | 04 §2.1, §1.18, §1.20; lab rules 2 and 5; §1.21 (RB 2016 re-save gave "invalid target namespace" on cloud; current behavior UNVERIFIED) | 3–14 h |
| **Rebuild as BAQ Report** | The output is a formatted document (statement, certificate, commission sheet) and today it uses direct SQL, Crystal or a stored procedure. Or it is a BAQ Report with a structural defect (missing Company join, release join multiplying rows). | One BAQ + BAQ Report (dataset reads `BAQReportResult_<GUID>`). For multi-dataset or sub-report layouts, an RDD with BAQ data sources. Server logic goes in an Epicor Function, not a stored procedure. Calculations go in BAQ calculated fields (T-SQL expression syntax). | 04 §2.2, §2.3, §2.7, §2.11; lab rules 1–3. Limits: §2.4 (no MES), §2.5 (some built-in RDD behavior cannot be reproduced with BAQs) | 10–24 h |
| **Replace with Grid** | Users only need rows on screen or a spreadsheet export, not a printed layout. This is common for "slow BAQ" and "export to the file share" items. | A BAQ the user runs and exports. File output, if still needed: write to a Sandbox folder (UserData/CompanyData) and retrieve it with Server File Download. Use **Get Query Execution Plan** for performance; you cannot add indexes. | 04 §2.11, §2.12, §2.8, §1.8–1.10 (first release where Sandbox.IO works: CONFLICTING) | 4–8 h |
| **Retire** | No runs, no owner, a duplicate, or the need has moved outside the ERP (e.g. a Power BI feed). | Archive the RDL/RPT and the BAQ definition. For analytics outside SSRS, the read-only replica is a separate paid option with its own limits (allow-listed IPs, ODBC only, no views, no BAQs, some tables locked). Quote it separately. | 04 §1.4, §2.9 | 0.5–2 h |

"Replace with Grid" means a BAQ shown as rows and exported. Exact Kinetic grid and
dashboard screens are not covered by the reference (dashboards are bucket C, parked).
Do not promise a specific screen.

## Step 3: risk and cloud-readiness values

Use the same values in the inventory so the sheet can be filtered.

| Cloud-Readiness | Meaning |
|-----------------|---------|
| Ready | Uses only RDD + RDL or BAQ paths (04 §2.1–2.3). |
| Needs check | A fact must be confirmed first, e.g. which RDD the base style uses (standing question e; `decisions.md` ARInvoice vs ARForm). |
| Needs change | Works on-prem, but uses a pattern 04 marks as warned or restricted (System.IO §1.7). |
| Blocked | Direct SQL, own SQL data source or stored-procedure dataset (04 §1.1, §1.2, §1.17). |

| Risk | Rule of thumb |
|------|---------------|
| High | Blocked on cloud, or business-critical with no documented logic, or wrong numbers today. |
| Medium | Slow, suspected defect, or an unconfirmed base RDD. |
| Low | Standard form mod with a known RDD, in use, no defect seen. |

## Defect flags that change the estimate (from 02-baq.md)

Raise the estimate if any of these are present. Each is a known BAQ defect with a known fix.

| Symptom in the inventory notes | Defect | Fix |
|--------------------------------|--------|-----|
| "Other company's numbers show up" | 1: missing Company join | Add `Company = Company` to every relation |
| `CustNum = CustID` join, conversion errors, slow | 2: CustID joined to CustNum (int vs varchar; error 245) | Join CustNum to CustNum, or go through Customer |
| Totals about 2x on multi-release orders | 3: OrderRel join multiplying rows | Aggregate OrderRel first, or drop the join |
| Filter seems ignored | 4: criteria on the wrong subquery | Move the criteria to the subquery that feeds the output |
| "Late" uses OrderDate | 5: wrong date field (per ticket spec) | Use the date the ticket names (NeedByDate) |
| Percent shows 0 | 6: integer division | `CAST` an operand to DECIMAL; guard a zero denominator |

## What this matrix does not claim

- It does not say any report "will fail" on a given release. Cloud behavior is
  forum-sourced (04), and the client's release and deployment is standing question d.
- It covers no Crystal-specific Kinetic behavior. The reference has no source on
  Crystal. Crystal items are classed only by how they reach data (usually ODBC direct
  SQL, which is gate G3).
- Scheduling and e-mail delivery of reports are not covered by the reference. Scope
  them as a separate line item.
