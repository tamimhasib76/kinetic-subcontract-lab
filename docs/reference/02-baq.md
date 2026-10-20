# 02 — BAQ Designer: Structure, Calculated Fields, Criteria, SQL, Analyze/Test

Scope: ticket type 2 (BAQ correctness fixes).
Research date: 2026-10-20. Research method: WebSearch/WebFetch of public pages only.

## How to read this file

- **CONFIRMED**: a cited source says this. "Forum" means a community post on
  epiusers.help, not Epicor documentation. A CONFIRMED forum claim is only as
  strong as that post.
- **CONFLICTING**: cited sources disagree. Both are cited.
- **UNVERIFIED**: no source found. Do not build lab behavior on it.
- The release is noted when a source names one.
- No official Epicor BAQ Designer help page or user guide was reachable (see
  "Gated / unreachable sources" at the end). A Scribd copy of a "Kinetic BAQ
  Designer User Guide" (© 2023) exists, but its body did not load. It is listed
  as unreachable and is **not** cited for any claim.

## Sources

| ID | Title | URL | Post date(s) | Release named |
|----|-------|-----|--------------|---------------|
| B1 | Kinetic BAQ - Get Query Execution Plan | https://www.epiusers.help/t/kinetic-baq-get-query-execution-plan/116161 | 2024-06-25 | none (Kinetic category; "Pilot") |
| B2 | Simple method to convert BAQ query to SQL server | https://www.epiusers.help/t/simple-method-to-convert-baq-query-to-sql-server/54347 | 2019-04-04 to 2019-04-05 (pre-2022) | 10.2.300.9; 10.1.400.38 |
| B3 | Using more than one UnionAll type in a single BAQ | https://www.epiusers.help/t/using-more-than-one-unionall-type-in-a-single-baq/136318 | 2026-07-20 to 2026-08-04 | 2026.100.7 |
| B4 | BAQ Union/Union All - Help Needed | https://www.epiusers.help/t/baq-union-union-all-help-needed/74408 | 2021-01-12 to 2021-01-14 (pre-2022) | none (ERP 10) |
| B5 | Problems with the Kinetic BAQ Designer | https://www.epiusers.help/t/problems-with-the-kinetic-baq-designer/129822 | 2025-10-07 | 2024.2.19 (11.3.200.19) |
| B6 | Kinetic BAQ designer - can no longer have criteria on two different tables in the same subquery? | https://www.epiusers.help/t/kinetic-baq-designer-can-no-longer-have-criteria-on-two-different-tables-in-the-same-subquery/131819 | 2026-01-09 | 2025.2; 2025.2.7 cloud |
| B7 | Scalar function in BAQ Designer Calculate Field Editor | https://www.epiusers.help/t/scalar-function-in-baq-designer-calculate-field-editor/123858 | 2025-03-06 to 2025-03-16 | 2023.2.25; 2024.2 |
| B8 | BAQ Calculated field division | https://www.epiusers.help/t/baq-calculated-field-division/94013 | 2022-09-02 | none (Kinetic category) |
| B9 | BAQ - Calculated Field Returning 0 or 1 | https://epiusers.help/t/baq-calculated-field-returning-0-or-1/109234 | 2023-11-17 | none (ERP 10 category) |
| B10 | Rounding When I Don't Want it | https://www.epiusers.help/t/rounding-when-i-dont-want-it/73565 | 2020-12-10; 2023-12-18 | none (ERP 10) |
| B11 | Number of days between two dates | https://www.epiusers.help/t/number-of-days-between-two-dates/99064 | 2023-02-02 | none (ERP 10 category) |
| B12 | BAQ Calculated field using String_AGG with case statement | https://www.epiusers.help/t/baq-calculated-field-using-string-agg-with-case-statement/131860 | 2026-01-12 | none (Kinetic category) |
| B13 | BAQ skip condition if empty not working for name parameters in Kinetic | https://www.epiusers.help/t/baq-skip-condition-if-empty-not-working-for-name-parameters-in-kinetic-anyone-got-this-working/123272 | 2025-02-14 | none (Kinetic category) |
| B14 | BAQ Query Execution Plan | https://www.epiusers.help/t/baq-query-execution-plan/66482 | 2020-04-20 to 2020-04-23 (pre-2022) | none (ERP 10) |
| B15 | 10.2.300.5 BAQ Designer in 10.2 not providing error details | https://epiusers.help/t/10-2-300-5-baq-designer-in-10-2-not-providing-error-details/50494 | 2018-12-10 to 2018-12-11; 2023-01-26 to 2023-01-27 | 10.2.300.x |
| B16 | BAQ Returning 10k records, even though Remove Test Row Limit = TRUE | https://www.epiusers.help/t/baq-returning-10k-records-even-though-remove-test-row-limit-true/109283 | 2023-11-20 | none (Kinetic category) |
| B17 | Union 2 BAQ sub-queries, and join the result of that union to another table | https://www.epiusers.help/t/union-2-baq-sub-queries-and-join-the-result-of-that-union-to-another-table/46934 | 2018-08-15 to 2018-08-16 (pre-2022); reply 2025-10-10 | none (ERP 10) |
| B18 | Adding new field from BAQ to SSRS | https://epiusers.help/t/adding-new-field-from-baq-to-ssrs/107769 | 2023-10-06 to 2023-10-12 | 10.2 |
| B19 | Dates, Times, DateTimes, SQL, LINQ, and the Usual Confusion | https://www.epiusers.help/t/dates-times-datetimes-sql-linq-and-the-usual-confusion/135539 | 2026-06-17 | none. **The author says AI wrote much of the post and not every fact was tested.** Used only as supporting context, never as sole support. |
| M1 | / (Division) (Transact-SQL) — Microsoft Learn | https://learn.microsoft.com/en-us/sql/t-sql/language-elements/divide-transact-sql?view=sql-server-ver16 | ms.date 2017-03-15 (page updated 2026-10-19) | n/a (Microsoft doc) |

---

## 1. BAQ Designer structure: subqueries

| # | Claim | Exact value | Label | Source |
|---|-------|-------------|-------|--------|
| 1.1 | Each subquery in a BAQ has a type. Types named in sources: `TopLevel`, `InnerSubQuery`, `Union`, `UnionAll`, `CTE`; "RecursiveCTE" also appears. | `TopLevel`, `InnerSubQuery`, `Union` | CONFIRMED (forum, 2018) | B17 |
| | | `CTE`, `UnionAll`, "top level" | CONFIRMED (forum, 2026, 2026.100.7) | B3 |
| | | "RecursiveCTE" | CONFIRMED as a term used by a poster (forum, 2021); whether it is a separate type value is UNVERIFIED | B4 |
| 1.2 | Whether `Intersect` and `Except` subquery types exist. | — | UNVERIFIED | — |
| 1.3 | **TopLevel**: the subquery that produces the BAQ's output columns. One poster counts "3 subqueries (counting the TopLevel one)". | — | CONFIRMED (forum) for the existence and role; formal definition UNVERIFIED | B17 |
| 1.4 | **InnerSubQuery**: a subquery used inside another subquery. You can join a union result by wrapping it in another subquery; then it "will behave as any other query would". | — | CONFIRMED (forum, 2018) | B17 |
| 1.5 | **Union / UnionAll (concept)**: a union "will just layer them on top of each other". The unioned subqueries need the same fields. | — | CONFIRMED (forum, 2021) | B4 |
| 1.6 | **CTE (concept)**: "You need a CTE if you want them linked". A CTE lets you reference the same query and loop recursively. The pattern is CTE anchor + UnionAll subquery that adds levels + top level for display. | — | CONFIRMED (forum) | B4, B3 |
| 1.7 | When combining several unions, set parentheses on the **SubQuery List** (SubQueryList) tab to group the levels. | Tab name `SubQueryList` / "subquery list" | CONFIRMED (forum, 2018 and 2026) | B17, B3 |
| 1.8 | A union must roll up to a TopLevel or CTE; a plain subquery will not work. | — | UNVERIFIED (seen only in a search snippet; not on the fetched page) | — |
| 1.9 | Kinetic designer lets you test a subquery on its own and copy a subquery from another BAQ. | — | CONFIRMED (forum, 2024.2.19) | B5 |
| 1.10 | Copied subqueries ended up with linked criteria (Kinetic bug report). | — | CONFIRMED (forum, single poster, 2026) | B6 |

## 2. Table relations (joins)

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 2.1 | In the Kinetic designer, tables appear as tiles ("table widgets") on a **canvas**. Joins are drawn between them and show join type labels. | CONFIRMED (forum, 2024.2.19; 2025.2) | B5, B6 |
| 2.2 | BAQs support inner and left outer joins. | CONFIRMED (forum, 2019, 10.1.400.38) | B2 |
| 2.3 | Full list of join types offered in the Kinetic relation editor (inner / left / right / full / cross). | UNVERIFIED | — |
| 2.4 | Kinetic designer defects reported in 2024.2.19: moving tables or adding relations can add unintended relations unless the table is selected first; the join type is sometimes not shown for a new join; relationship drop-downs often stay empty until expanded repeatedly; clicking a relationship may select a different item. | CONFIRMED (forum, single thread) | B5 |
| 2.5 | A UnionAll subquery in a recursive CTE accepted a default join on revision number and gave wrong results; changing the join fixed it. | UNVERIFIED (search snippet only) | — |
| 2.6 | A numeric field from a left join showed `0` instead of null in Kinetic Run Query, which sent one user chasing joins that were correct. | CONFIRMED (forum, 2024.2.19) | B5 |

## 3. Display fields

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 3.1 | Display Fields uses **Available** and **Display** lists; you move fields between them. | CONFIRMED (forum, 2024.2.19) | B5 |
| 3.2 | Selecting several fields to move sometimes moves the wrong ones (Kinetic). | CONFIRMED (forum, single thread) | B5 |
| 3.3 | In Kinetic 2024.2.19 the `<` arrow no longer removes calculated fields; you must delete them in the editor. | CONFIRMED (forum, single thread) | B5 |
| 3.4 | Output column names in BAQ results and BAQ report staging are `<Table>_<Field>` and `Calculated_<Name>`, for example `Customer_CustID`, `Calculated_TodayDate`. | CONFIRMED (forum, 2023) | B18 |

## 4. Calculated fields and their syntax (answers question 8)

| # | Claim | Exact expression / value | Label | Source |
|---|-------|--------------------------|-------|--------|
| 4.1 | The editor is called the "Calculate Field SQL Editor" by a 2025 poster. Its Fields tree lets you pick current Display Fields and existing Calculated fields. | — | CONFIRMED (forum, 2023.2.25) | B7 |
| 4.2 | The Kinetic editor has a **Data and Functions** panel, which one user found too small. | — | CONFIRMED (forum, 2024.2.19) | B5 |
| 4.3 | Calculated fields accept SQL Server expression syntax: CASE/WHEN/THEN/ELSE/END and ISNULL. | `case when ISNULL(ShouldHaveTaken,0) <> 0 and ISNULL(LaborDtl.LaborHrs, 0) <> 0 then ((LaborDtl.LaborHrs - ShouldHaveTaken)/ShouldHaveTaken) else 0 end` | CONFIRMED (forum, 2022, Kinetic) | B8 |
| 4.4 | CAST with DECIMAL is accepted and fixed a 0 result. | `CAST(field1 AS DECIMAL(7,2) )/CAST(field2 AS DECIMAL(7,2) )` | CONFIRMED (forum, 2023) | B9 |
| 4.5 | DATEDIFF is accepted. `Constants.Today` can be used as an argument. The working form was `datediff(day, ...)`; an earlier `datediff(dd, ...)` attempt failed, but the poster blamed BAQ configuration, not the `dd` keyword. Calculated field data type: Integer. | `datediff(day, RMAHead.RMADate, Constants.Today)` | CONFIRMED (forum, 2023) | B11 |
| 4.6 | CONVERT is accepted (`convert(int, datediff(...))`). In that thread it did not fix the error, which had another cause. | `convert(int,datediff(dd, RMAHead.RMADate, Constants.Today))` | CONFIRMED (forum, 2023) that it was entered; that it runs is UNVERIFIED | B11 |
| 4.7 | STRING_AGG with a nested CASE is accepted. Enter **only the expression**: an `AS <alias>` at the end causes "incorrect syntax". | — | CONFIRMED (forum, 2026, Kinetic) | B12 |
| 4.8 | `getdate()` inside CASE was suggested as a null-safe alternative. | `CASE WHEN (RMAHead.RMADate) is null THEN 0 ELSE datediff(dd, RMAHead.RMADate, getdate()) END` | CONFIRMED (forum, suggestion only; not confirmed working) | B11 |
| 4.9 | Epicor scalar functions (examples `Ice.Entry()`, `GetCustID`) were removed from the editor's function menu in 2023.2 and 2024.2, but can still be typed in and work. | — | CONFIRMED (forum, 2025) | B7 |
| 4.10 | The editor's **documented function list** (official Epicor help). | — | UNVERIFIED: official BAQ Designer guide not reachable; no source lists the menu contents in text | — |
| 4.11 | Referring to another calculated field: the original expression used the bare name `Shouldhavetaken`. A suggestion to use `Calculated_shouldhavetakein` gave "invalid column name". | — | CONFLICTING / unresolved: B8 shows both forms and neither is confirmed as the fix | B8 |
| 4.12 | Divide-by-zero: a zero or null denominator causes an error. Guard with CASE/ISNULL in the denominator. | — | CONFIRMED (forum) | B8, B9 |
| 4.13 | Is the editor a SQL expression editor, or another language (C#/LINQ)? | — | See answer (8) | — |

### Integer division

- T-SQL rule: "If an integer dividend is divided by an integer divisor, the result is an integer that has any fractional part of the result truncated." CONFIRMED (Microsoft doc) — M1.
- In BAQs: 24/28 returned 0. The fix was to CAST both operands to DECIMAL before dividing. CONFIRMED (forum, 2023) — B9.
- Counts used in later calculated fields must be cast to decimal first. CONFIRMED (forum, 2020/2023) — B10.
- Setting only the calculated field's display type or format to decimal does not change the arithmetic. Inferred from M1 and B10 ("cast the count as decimal if you want to use it in another calculated field"). UNVERIFIED as a stated rule.
- Another fix is multiplying by a decimal literal such as `1.0` or dividing by `60.0`. B8's own expression uses `* 1.0`; B19 recommends `60.0` (B19 is weak, see source note). CONFIRMED by B8's working usage only as "entered". Its effect follows from M1 data-type precedence. UNVERIFIED as a tested BAQ result.

## 5. Criteria

| # | Claim | Exact value | Label | Source |
|---|-------|-------------|-------|--------|
| 5.1 | There are two criteria levels: **Table Criteria** (on a table in a subquery) and **SubQuery Criteria**. "Table criteria" is a BAQ concept, not a SQL one. | — | CONFIRMED (forum, 2026) | B6, B5 |
| 5.2 | Parameters are named with `@`, for example `@IDP_FullName`. Each has **Skip Condition If Empty** and **Mandatory** settings. | — | CONFIRMED (forum, 2025) | B13 |
| 5.3 | Skip Condition If Empty only skips simple conditions such as `value = @parametername`. A complex expression with empty parameters gave "Bad SQL statement". Workaround: `LIKE` with `'%' + @p + '%'`, so an empty value matches everything. | — | CONFIRMED (forum, 2025) | B13 |
| 5.4 | Do not set both Mandatory and Skip Condition If Empty. | — | CONFIRMED (forum, single poster) | B13 |
| 5.5 | Choosing "specified parameter" (vs "specified expression") makes parameters selectable in table criteria. | — | UNVERIFIED (search snippet only) | — |
| 5.6 | Kinetic 2025.2: criteria intermittently could not be set on two different tables in the same subquery. Others could not reproduce it; re-importing the BAQ under a new name fixed it. | — | CONFIRMED (forum, report) / CONFLICTING (not reproducible by others) | B6 |
| 5.7 | Criteria order sometimes changed after reopening ("x and y" became "y, x"), and then the BAQ stopped executing (Kinetic 2024.2.19). | — | CONFIRMED (forum, single thread) | B5 |
| 5.8 | Calculated fields are hard to find in SubQuery Criteria (one user could not find them). | — | CONFIRMED (forum, 2022) | B8 |

## 6. How the BAQ compiles to SQL

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 6.1 | The designer shows the generated statement as the **Query Phrase** (classic path: BAQ > Summary > Query Phrase). | CONFIRMED (forum, 2019, 10.1.400.38); Kinetic location UNVERIFIED | B2 |
| 6.2 | The SQL actually executed is not the Query Phrase alone. Epicor appends extra checks in the background, for example territory and sales rep checks whenever a Customer table is included; "your query is only a part of the executed query". | CONFIRMED (forum, 2019) | B2 |
| 6.3 | The Query Phrase showed cross joins where the user had built inner and left outer joins. | CONFIRMED (forum, 2019, single poster) | B2 |
| 6.4 | Epicor references views rather than raw tables. Use `Erp.`/`Ice.` schema prefixes, or `dbo.` when UD columns are involved, to reproduce in SSMS. | CONFIRMED (forum, 2019) | B2 |
| 6.5 | Calculated fields relate differently in Epicor than in a hand-written SQL query ("will trip you up"). | CONFIRMED (forum, 2019; detail unspecified) | B2 |
| 6.6 | Does the Kinetic web designer generate the same SQL as Classic for the same BAQ? | CONFLICTING: "BAQs execute on the server regardless of UI version" (Olga Klimova) vs "classic composes the WHERE clause correctly, Kinetic does not" (Alisa Osemwengie) | B6 |
| 6.7 | You cannot paste SSMS SQL into the BAQ designer to create a BAQ. | CONFLICTING: one poster (10.1.400.38) copied the Query Phrase out; another (10.2.300.9) could not paste SQL in. Pasting SQL in is not supported by any source. | B2 |
| 6.8 | BAQ constants (`Constants.Today`) and parameters (`@Name`) are BAQ tokens replaced before SQL runs. | UNVERIFIED (they are accepted in expressions per B11 and B13; the replacement mechanism is not documented in any source found) | — |
| 6.9 | The outer SQL is built by the designer; you supply expressions and criteria. | UNVERIFIED as a sole claim: stated only in B19, which is AI-assisted and untested by its author. Consistent with B12 (enter only the expression). | B19, B12 |

## 7. Analyze and Test behavior

| # | Claim | Label | Source |
|---|-------|-------|--------|
| 7.1 | **Test** runs the standard Execute BAQ logic. Since 10.2.300 security hardening it returns only a generic "Bad SQL statement" message, and the real SQL error is logged on the server (Event Viewer → Applications and Services Logs → Epicor App Server). | CONFIRMED (forum, 2018 statement by an Epicor-side poster; 2023 path) | B15 |
| 7.2 | **Analyze** sends the query to SQL for a syntax check. Its error should match the logged error, so use Analyze to see the actual error text. | CONFIRMED (forum, 2018) | B15 |
| 7.3 | Analyze can return "Syntax is OK" while Test returns "Bad SQL statement". | CONFIRMED (forum, 2023) | B15 |
| 7.4 | **Get Query Execution Plan** needs a successful Test first ("hit Test, not Analyze"). | CONFIRMED (forum, 2020) | B14 |
| 7.5 | In Kinetic the plan downloads as a `.sqlplan` file; open it in SSMS or Plan Explorer. On cloud you cannot add indexes. One user could use it in Pilot but not before. | CONFIRMED (forum, 2024) | B1 |
| 7.6 | The plan is a picture of the executed SQL, not the SQL text. Use SQL Profiler to capture text (on-prem only). | CONFIRMED (forum, 2019) | B2 |
| 7.7 | The test result was capped at 10,000 rows even with `RemoveTestRowLimit` = TRUE. One poster: the flag only matters outside the analyzer. Another: there is no limit outside the tester even without the flag, and a server setting was the cause. | CONFLICTING | B16 |
| 7.8 | Kinetic name for running results: **Run Query**. It lacks Show Summaries and Group By counts (2024.2.19), and the % display format is ignored. | CONFIRMED (forum, single thread) | B5 |
| 7.9 | Some BAQs analyze or execute in the Classic client but fail in the Kinetic designer. | CONFIRMED (forum, single thread, 2024.2.19) | B5 |
| 7.10 | Kinetic designer button labels for Analyze and Test (exact text and location). | UNVERIFIED | — |

---

## Phase 2b fix-drill defects

Seeded BAQ defects for the Phase 2b fix drills. Items 1–5 were set by the
project owner on 2026-10-20 (`decisions.md`); item 6 was added at checkpoint 2.
The defect list is a project decision. The "Source" column only says whether a
cited source supports the mechanism; where none does, the mechanism is UNVERIFIED
in this research and rests on the project owner's definition.
S-IDs are sources in `01-ssrs-forms.md`; D-IDs are sources in `03-dmt.md`.

| # | Defect | Fix | Source |
|---|--------|-----|--------|
| 1 | **Missing Company join**: a relation omits `Company`, so rows from other companies bleed in. | Add `Company = Company` to every table relation. | Project owner. RDD joins always include Company in cited queries (S19, S17); BAQ-specific UNVERIFIED |
| 2 | **CustID joined to CustNum**: an int/varchar mismatch. It can cause a non-numeric conversion error, silent wrong matches, or a slow scan. | Join `CustNum` to `CustNum`, or join through Customer to get CustID. | Project owner. CustNum is the internal ID and CustID the editable ID (D10); conversion behavior UNVERIFIED (no T-SQL doc fetched) |
| 3 | **Release join multiplying rows**: joining OrderRel to OrderDtl returns one row per release, so line totals are counted more than once. | Aggregate OrderRel in a subquery first, or do not join it when only line data is needed. | Project owner. Extra joins duplicated report rows in S17/S13; BAQ-specific UNVERIFIED |
| 4 | **Criteria on the wrong subquery**: the filter sits on a subquery that does not limit the output. | Move it to Table Criteria / SubQuery Criteria of the subquery that feeds the output. | Project owner; criteria levels in B6, B5 |
| 5 | **Wrong date field**: `OrderDate` used instead of `NeedByDate`. | Use `NeedByDate` for due-date logic. | Project owner. `NeedByDate` and `OrderDate` both appear as OrderHed DMT columns (D7, D3); field semantics UNVERIFIED |
| 6 | **Integer division truncation**: a calculated field divides two integers (for example two counts), so 24/28 returns 0. | Cast an operand to DECIMAL before dividing, e.g. `CAST(a AS DECIMAL(7,2)) / CAST(b AS DECIMAL(7,2))`. Guard a zero/NULL denominator with CASE/ISNULL. | M1, B9, B10, B8 |

---

## Answer (8): Calculated field language and integer division

**Is the expression SQL?** Yes, by every source found. It is written as a
SQL Server (T-SQL) scalar expression, not C# or LINQ. The evidence:

- Working examples use T-SQL only: `CASE … WHEN … THEN … ELSE … END`, `ISNULL` (B8), `CAST(… AS DECIMAL(7,2))` (B9), `datediff(day, …)` (B11) and `STRING_AGG(CASE … END, ', ')` (B12). CONFIRMED (forum).
- A 2025 poster calls the editor the "Calculate Field SQL Editor". CONFIRMED (forum) — B7.
- Integer division behaves exactly as T-SQL documents (B9 vs M1). CONFIRMED.
- You enter only the expression, with no `SELECT` and no `AS` alias. CONFIRMED (forum) — B12.
- The expression can also contain BAQ-specific tokens, `Constants.Today` (B11) and `@Parameter` names (B13), and Epicor scalar functions such as `Ice.Entry()` and `GetCustID` (B7). CONFIRMED (forum).

**Does it work because "the BAQ compiles to SQL"?** That the BAQ produces SQL
is CONFIRMED (Query Phrase and executed SQL, B2). The exact pipeline (whether
the expression text is inserted verbatim into the SELECT list) is **UNVERIFIED**.

**Documented function list:** **UNVERIFIED.** The official Epicor guide was not
reachable, and the editor's function menu changed in 2023.2/2024.2 (B7). No
public source lists its contents in text.

**Integer division:** integer / integer truncates the fractional part (M1).
In a BAQ, 24/28 returned 0 (B9). Cast at least one operand to DECIMAL (B9, B10)
before dividing, and guard the denominator against 0/NULL with CASE/ISNULL
(B8, B9). CONFIRMED.

---

## Gated / unreachable sources (for this file)

- Epicor Kinetic BAQ Designer User Guide / ICE Tools User Guide: EpicWeb login required; not attempted. A Scribd copy (https://www.scribd.com/document/720590765/Kinetic-BAQDesignerUserGuide) returned only a "required part of this site couldn't load" page.
- Epicor Kinetic Application Help for BAQ Designer (Calculated Field Editor, Analyze/Test): no public URL found.
- epicor.com BAQ product page (https://www.epicor.com/en/products/enterprise-resource-planning-erp/epicor-kinetic/tools-and-technology/business-activity-queries/): HTTP 403 to WebFetch.
- EpicCare knowledge base: login required; not attempted.
