# 04 — Kinetic Multi-Tenant Cloud: What Is Blocked, and Cloud-Safe Report Alternatives

Scope: rules every report, BAQ and DMT ticket must respect on Epicor Kinetic
public (multi-tenant) cloud.
Research date: 2026-10-20. Research method: WebSearch/WebFetch of public pages only.

## How to read this file

- **CONFIRMED**: a cited source says this. "Forum" means a community post on
  epiusers.help. "Epicor staff" means a post by an Epicor employee on the forum,
  not product documentation.
- **CONFLICTING**: cited sources disagree. Both are cited.
- **UNVERIFIED**: no source found.
- No Epicor cloud policy document was reachable. The Cloud SDK page on epicor.com
  returned HTTP 403, and the Kinetic help topic "Accessing Resources Using the
  Sandbox Property" is cited second-hand only (C7). Every CONFIRMED item below
  rests on forum posts.

## Sources

| ID | Title | URL | Post date(s) | Release named |
|----|-------|-----|--------------|---------------|
| C1 | SQL query to pull data directly from SSRS - Kinetic Pilot SaaS | https://www.epiusers.help/t/sql-query-to-pull-data-directly-from-ssrs-kinetic-pilot-saas/99778 | 2023-02-22 to 2023-03-01 | none (SaaS Pilot) |
| C2 | Cloud Direct SQL Access | https://www.epiusers.help/t/cloud-direct-sql-access/132332 | 2026-01-28 to 2026-01-29 | none (cloud SaaS) |
| C3 | Epicor ERP Cloud Production Environment Copy for Read-Only Data Access | https://www.epiusers.help/t/epicor-erp-cloud-production-environment-copy-for-read-only-data-access/88478 | 2022-03-15 to 2023-05-26 | none |
| C4 | Calling database stored procedure | https://www.epiusers.help/t/calling-database-stored-procedure/83184 | 2021-10-04 (pre-2022) | none (Kinetic category) |
| C5 | Compiler Warning when saving BPM after recent Kinetic updates | https://www.epiusers.help/t/compiler-warning-when-saving-bpm-after-recent-kinetic-updates/111289 | 2024-01-31 to 2024-07-15 | Kinetic Cloud 2023.2.9 |
| C6 | These warnings will become errors in the future (post #57, Epicor staff) | https://www.epiusers.help/t/these-warnings-will-become-errors-in-the-future/117505/57 | 2024-09-06 | 2024.2 |
| C7 | Sandbox.IO in Functions Workflows | https://www.epiusers.help/t/sandbox-io-in-functions-workflows/130344 | 2025-10-28 to 2025-12-29 | 2025.1; 2025.2.x |
| C8 | System.IO | https://www.epiusers.help/t/system-io/108953 | 2023-11-08 to 2023-11-22 | 2023.2.5 |
| C9 | Getting Cloud ready - setting up connection to local fileserver for Kinetic 2025.2 | https://www.epiusers.help/t/getting-cloud-ready-setting-up-connection-to-local-fileserver-for-kinetic-2025-2/136175 | 2026-07-14 to 2026-07-16 | 2025.2 |
| C10 | SSRS report design: Really? | https://www.epiusers.help/t/ssrs-report-design-really/108159 | 2023-10-18 to 2023-10-25 | none (Kinetic category) |
| C11 | File Save from epicor functions | https://epiusers.help/t/file-save-from-epicor-functions/110173 | 2023-12-20 to 2023-12-21 | none (Kinetic category) |

This file also uses sources from `01-ssrs-forms.md` (S-IDs) and `02-baq.md` (B-IDs).

---

## 1. What multi-tenant cloud blocks

### 1a. Direct SQL

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 1.1 | You cannot run SQL directly against the Kinetic database in cloud SaaS ("No, you cannot do SQL in cloud"). Integrations should use REST. | CONFIRMED (forum, 2026, several posters) | C2 |
| 1.2 | An SSRS report that queries the ERP database directly (its own SQL data source) is "not a supported Epicor configuration". One poster says it can be made to work in a hosted environment, unsupported. | CONFLICTING: not supported (C1, Kevin Lincecum) vs "it works in hosted environment" (C1, Mike Tonoyan). Lab rule: treat it as blocked. | C1 |
| 1.3 | Reason for the restriction: the SQL service principal has access to the whole Epicor database, which would bypass application security. The report pipeline instead uses least-privilege temp tables that are deleted after a set period. | CONFIRMED (forum, 2023) | C10 |
| 1.4 | Paid option: a read-only replica (RODB). It is near real time, but not all tables are available (system and PII tables are locked). You get one or two accounts, connections come from allow-listed IPs, it is ODBC only, you cannot create views on it, and you cannot call BAQs through it. | CONFIRMED (forum, 2022–2026) | C3, C2 |
| 1.5 | Can SQL views be added as RDD data sources? | UNVERIFIED (asked in C1; no answer) | C1 |
| 1.6 | Reading the report-database GUID tables directly (as in on-prem design with `TableGuid`) is not possible on SaaS. | UNVERIFIED (seen in a search snippet only; the fetched page did not contain it) | — |

### 1b. File system

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 1.7 | Custom code (BPMs, Functions) using `System.IO` gets warnings (`ECF1002`) such as for `File.AppendAllText` and `GZipStream`. Epicor staff say the warnings are intentional (security, performance, data integrity) and "will become errors". | CONFIRMED (forum + Epicor staff, 2024; Kinetic Cloud 2023.2.9) | C5 |
| 1.8 | From 2024.2 a **Sandbox** class provides System.IO counterparts that take a path class (server locations) instead of an arbitrary path. It is available in Functions, Data Directives and Method Directives. | CONFIRMED (Epicor staff, 2024-09-06) | C6 |
| 1.9 | Use `this.Sandbox.IO` in a Function; no reference is needed. The help page "Accessing Resources Using the Sandbox Property" lists server folders **UserData** and **CompanyData**; writing to **FileShare** also works (poster). | CONFIRMED (forum, 2025) for UserData/CompanyData via help page as quoted; FileShare UNVERIFIED | C7 |
| 1.10 | First release where `Sandbox.IO` works. | CONFLICTING: 2024.2 (C6) vs "at least 2025.1" (C7) vs assembly "not cooked into the Framework until 2025.2.x" (C7) | C6, C7 |
| 1.11 | 2025.2.x appears to be removing System.IO features Epicor considers cloud-unfriendly. | CONFIRMED (forum, single poster, 2025-12-29) | C7 |
| 1.12 | Function libraries using restricted features are disabled after an upgrade. | CONFLICTING: stated, then retracted by the same poster as an incorrect assumption | C5 |
| 1.13 | `System.Reflection` is not supported in custom code (it uses non-public APIs). | CONFIRMED (Epicor staff, 2024) | C6 |
| 1.14 | Browser-based Kinetic cannot reach local files directly (browser sandbox). The Edge Agent, a local web service, does file access for the browser. | CONFIRMED (forum, 2026; 2022) | C9, S3 |

### 1c. Stored procedures

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 1.15 | From the Kinetic web interface there is no known way to call a stored procedure directly. In cloud, an external option is Logic Apps behind a secured API. | CONFIRMED (forum, 2021) | C4 |
| 1.16 | Stored procedures can be called from BPM, Function or WinForms customization (on-prem); not recommended. Prefer an Epicor Function, "which would be supported". | CONFIRMED (forum, 2021) | C4 |
| 1.17 | An SSRS dataset of type stored procedure (on-prem pattern) is blocked on multi-tenant cloud. | UNVERIFIED as a stated rule. It follows from 1.1–1.2 (no direct SQL), but no source says it about SSRS stored procedures. | — |

### 1d. SSRS-specific cloud limits (from 01-ssrs-forms.md)

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 1.18 | Cloud custom report names are no longer allowed. Use the names from the downloaded zip, starting from a copy of the out-of-box style. | CONFIRMED (forum, relaying support, 2025) | S9 |
| 1.19 | In 2024.1+, custom reports are stored in `Ice.CustomReportStore`; base reports are in the read-only IceCommon database. | CONFIRMED (forum, 2024) | S10 |
| 1.20 | Cloud zip upload rules (`reports.zip`, path = Report Location). | CONFIRMED (forum) | S7, S5 |
| 1.21 | Re-saving an RDL in Report Builder 2016 and uploading to cloud failed with "invalid target namespace". | CONFIRMED (forum, 2021); current behavior UNVERIFIED | S30 |

## 2. Cloud-safe alternatives for reports

| # | Alternative | When to use | Label | Source |
|---|-------------|-------------|-------|--------|
| 2.1 | **Modify the standard RDD + RDL**: duplicate the RDD, un-exclude columns, add linked tables or relationships, then edit the RDL dataset query (`<Table>_" + Parameters!TableGuid.Value + "`). | Add fields to a standard form (PackSlip, OrderAck, ARForm) | CONFIRMED (forum) | S15, S12, S17 |
| 2.2 | **BAQ Report**: build a BAQ, then a BAQ Report. The dataset reads `BAQReportResult_<GUID>`. | Custom list-style reports with no direct SQL | CONFIRMED (forum) | C1, S26, S27 |
| 2.3 | **RDD with BAQ data sources** ("Advanced BAQ Report"): one or more BAQs as RDD data sources, Report Type "SQL Server Reporting", output location "database". | Multi-dataset or sub-report layouts on cloud | CONFIRMED (forum, 2023 and 2026) | C10, S32 |
| 2.4 | Limit of 2.3: a BAQ-based RDD becomes a Dynamic Criteria Report, which cannot be added to MES (idea KIN-I-4055). | — | CONFIRMED (forum, 2023) | C10 |
| 2.5 | Limit of 2.3: some built-in RDD behavior is very hard or impossible to reproduce with BAQs. Then modifying the built-in report is the only option. | — | CONFIRMED (forum, 2023) | C10 |
| 2.6 | **RDD linked tables / calculated fields** to supply extra data without a manual link. This did not work for one user's case. | — | CONFIRMED (forum, 2023) | C1 |
| 2.7 | **Epicor Functions** instead of stored procedures for server logic. | Logic that would have been a stored procedure | CONFIRMED (forum, 2021) | C4 |
| 2.8 | **File output**: write to an EpicorData folder (CompanyData/UserData via Sandbox), then the user retrieves it with **Server File Download**. | Exports instead of file-system writes | CONFIRMED (forum, 2023 and 2025) | C11, C7 |
| 2.9 | **Read-only replica + external tool** (Access/ODBC, Power BI) for reporting outside SSRS. Extra cost. | Heavy analytics | CONFIRMED (forum) | C3, C2 |
| 2.10 | **REST / BAQSvc** for integrations instead of SQL polling. | Integrations | CONFIRMED (forum, 2026) | C2 |
| 2.11 | BAQ calculated fields in T-SQL expression syntax are allowed on cloud (they run inside the BAQ). | Calculations without direct SQL | CONFIRMED (forum; B8 is in the Kinetic category, cloud not stated) | B8, B9, B11 |
| 2.12 | Show query cost on cloud with BAQ **Get Query Execution Plan** (`.sqlplan`); you cannot add indexes. | Performance tickets | CONFIRMED (forum, 2024) | B1 |

## 3. Lab rules derived from the above

These are lab rules, not Epicor statements. Each is tied to the claims it rests on.

1. No RDL in this lab may use a direct SQL connection to the ERP database or a stored-procedure dataset (1.1, 1.2, 1.17).
2. Every report change goes through RDD + RDL (2.1) or BAQ / BAQ-based RDD (2.2, 2.3).
3. Server logic goes in an Epicor Function, never a stored procedure (1.15, 1.16, 2.7).
4. No `System.IO` with arbitrary paths. Use Sandbox folders and Server File Download (1.7–1.10, 2.8).
5. After every upload or Publish, re-download and verify (01-ssrs-forms.md §7c).

---

## Gated / unreachable sources (for this file)

- Epicor Cloud SDK product page (https://epicor.com/en/products/enterprise-resource-planning-erp/kinetic/cloud-business-platform/cloud-sdk): HTTP 403 to WebFetch.
- Kinetic help topic "Accessing Resources Using the Sandbox Property": cited by C7; no public URL found.
- Epicor cloud customer policy / SaaS service description documents: not found publicly; EpicWeb/EpicCare login required.
- Santiago Palacios' GitHub gist of Sandbox.IO methods (https://gist.github.com/Epic-Santiago/b842d06370cb56d2b1af43ae1f45f5e8): seen in search results, not fetched; not cited.
