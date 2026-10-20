# SyteLine to Kinetic Bridge: Orders, Parts, Customers

A mapping guide for moving order, part and customer data from SyteLine (CSI) tables
into Kinetic DMT files. It is the "where does this column go" sheet for the DMT
validator kit (`dmt-validator/`).

## Evidence levels: read this first

- **Kinetic side:** column names and rules are cited from `docs/reference/03-dmt.md`
  ([D#]) and `02-baq.md` (fix-drill defects; [M#]). Bucket A defaults carry the
  banner **"Default chosen for the lab, not confirmed against Epicor."**
- **SyteLine side: UNVERIFIED.** The project reference contains **no SyteLine
  source**. The SyteLine table and column names below (`co_mst.co_num`,
  `custaddr_mst.cust_seq`, ...) come from general practitioner knowledge, not from
  a cited source. Confirm each one against the client's SyteLine database (read-only,
  on a copy) before building an extract.
- The mapping choices (which SyteLine column feeds which Kinetic column) are lab
  design. They are not Epicor or Infor statements.

## The two rules that break most migrations

### Rule 1: the Company join rule

In Kinetic, every join between tables includes `Company`. A join that leaves it out
lets rows from another company bleed in (02-baq.md, fix-drill defect 1; project
decision. RDD joins always include Company in the cited queries S19, S17).

What this means for the bridge:
- Decide, in writing, how each SyteLine site (`site_ref`, UNVERIFIED) maps to a
  Kinetic **Company** and **Plant**. One SyteLine site may become a Kinetic Company,
  or a Plant inside one. Put the answer in a site map (Company, Plant, WarehouseCode)
  like `dmt-validator/sample-dirty-csvs/reference/sites.csv`.
- Every extract query joins on site as well as on the business key. Every Kinetic
  file row carries `Company`.
- The same CustID or PartNum can exist in two companies (MFG01 and MFG02 in the
  sample). They are different records. A PartPlant row in MFG01 does not set up the
  part in MFG02. The validator's `PARTPLANT_MISSING_FOR_SITE` check names this case.

### Rule 2: the CustNum (int) vs CustID (string) trap

| | Kinetic `CustNum` | Kinetic `CustID` | SyteLine `cust_num` (UNVERIFIED) |
|---|---|---|---|
| Type | integer | string | string. Commonly right-justified with leading spaces, e.g. `'   1001'`. Confirm on the client DB |
| Role | internal number [D10] | editable, user-facing ID [D10] | user-facing customer number |
| In DMT files | lookup columns resolve it for you: `CustNumCustID`, `CustomerCustID` [D11][D8] | what you type | becomes **CustID** (trimmed) |

- Map SyteLine `cust_num` to Kinetic **CustID**, trimmed. **Never** map it to
  `CustNum`, even when it looks numeric. Kinetic CustNum is Kinetic's own internal
  number; the same CustID carries a different CustNum in each company (see the
  sample data).
- Give the customer to DMT through `CustNumCustID` (ShipTo and others) or
  `CustomerCustID` (Sales Order). DMT resolves CustNum ([D11][D8], 03-dmt.md 1.5).
- Trim it. A hidden character after a CustID caused "Invalid Sold To" on a
  `CustNumCustID` lookup ([D12], 03-dmt.md §6 #6). Leading spaces in a padded
  `cust_num` are the same class of problem.
- In SQL, never join or compare a CustID (varchar) column to a CustNum (int) column.
  `int` outranks `varchar`, so SQL Server converts the varchar side to int. A value
  like `ACME01` then fails with error 245; numeric-looking values match the wrong
  rows silently ([M2][M3]; 02-baq.md defect 2). Use `TRY_CONVERT` when you must test.

---

## Map 1: orders. `co_mst` / `coitem_mst` to OrderHed / OrderDtl / OrderRel

SyteLine holds one `coitem_mst` row per order line **and release**
(`co_num`, `co_line`, `co_release`; UNVERIFIED). Kinetic splits that into OrderDtl
(one per line) and OrderRel (one per release). So:

- **OrderHed** = one row per `co_mst` row.
- **OrderDtl** = one row per distinct (`co_num`, `co_line`).
- **OrderRel** = one row per `coitem_mst` row.

| Kinetic column | Cited? | From SyteLine (UNVERIFIED) | Notes |
|----------------|--------|----------------------------|-------|
| OrderHed `Company` | [D8] | site map of `co_mst.site_ref` | Rule 1 |
| OrderHed `OrderNum` | [D8] | `co_mst.co_num` (if numeric) or `0` | `0` with Add makes the system assign the number [D6][D7] (03-dmt.md 2.5). SyteLine order numbers are often alphanumeric; if so, keep the old number in a reference field and let Kinetic assign. Where to keep it is not cited |
| OrderHed `CustomerCustID` | [D8]; default 57 (banner) | `co_mst.cust_num`, trimmed | Rule 2 |
| OrderHed `CustNum` | Kinetic 2025 suggestion only [D3] | **leave blank** | Rule 2. The validator's `CUSTNUM_NOT_INT` catches a CustID here |
| OrderHed `PONum` | suggested header [D3] | `co_mst.cust_po` | A new order number is assigned at each PONum change if duplicate-PO checking is on [D6][D7] |
| OrderHed `OrderDate`, `RequestDate`, `NeedByDate` | headers seen [D3][D7] | `co_mst.order_date`; due dates | Which date a report or rule needs comes from the ticket spec (defect 5) |
| OrderDtl `OrderLine` | `OrderDtl#OrderLine` [D8] | `coitem_mst.co_line` | Distinct per order; restarting at 1 starts a new order [D6]. Kits use up line numbers [D5] |
| OrderDtl `PartNum` | `OrderDtl#PartNum` [D8] | `coitem_mst.item` | The part must be loaded first (default 59, banner) |
| OrderDtl `LineDesc` | `OrderDtl#LineDesc` [D8] | `item_mst.description` or the line's own description | |
| OrderDtl `SellingQuantity` | posted as `OrderDtl#SellingQuantiy` [D8] | sum of `coitem_mst.qty_ordered` over the line's releases | How to roll release quantities up to a line is a lab choice; confirm with the client |
| OrderDtl unit price | `OrderDtl#DspUnitPrice` [D22] | `coitem_mst.price` | `DocUnitPrice` loaded as 0 for one poster [D22]. If releases of one line have different prices, it cannot be one OrderDtl price; raise it as a question |
| OrderRel `OrderRelNum` | `OrderRel#OrderRelNum` [D8] | `coitem_mst.co_release` | Multi-line orders gave "Invalid OrderRelNum" on the last line, unresolved [D3] |
| OrderRel site | not cited (`OrderRel#Plant` in the kit is lab layout) | `coitem_mst.ship_site` or `site_ref`, through the site map | The part needs a PartPlant row for that Company and site (validator check) |

## Map 2: parts. `item_mst` to Part / PartPlant / PartWhse

Load order: Part, then PartPlant, then PartWhse ([D19], 03-dmt.md 4.3; [D20] 4.4).
UOM classes and conversions must exist before Part ([D13], 4.6). Warehouses must exist
in the site before PartPlant ([D9], 4.7).

| Kinetic | Cited? | From SyteLine (UNVERIFIED) | Notes |
|---------|--------|----------------------------|-------|
| Part `PartNum` | [D14] | `item_mst.item`, trimmed | Same item at several SyteLine sites becomes **one** Part per Kinetic Company plus one PartPlant per site |
| Part `PartDescription` | [D14][D15] | `item_mst.description` | Required even on update [D14][D15] |
| Part `IUM`, `PUM`, `SalesUM` | [D13] | `item_mst.u_m` (and purchase/sales UM if different) | Must be codes in the Kinetic UOM class. Map codes (`EA` vs `EACH`) in a UOM map first [D13]. Trim them (validator `WHITESPACE`) |
| Part `TypeCode` | default 53: warn if missing (banner) | `item_mst.p_m_t_code` | The value mapping (e.g. M/P) is not cited; confirm |
| Part `ClassID` | must be a code, not a description [D14] | `item_mst.product_code` | Codes, not descriptions (`FG`, not `Finished Goods`) [D14] |
| PartPlant `Company`, `PartNum`, `Plant` | default 54 (banner) | site map of `item_mst.site_ref` | One row per site the part is used in |
| PartPlant `PrimWhse` | [D9] | the site's default warehouse (e.g. from `itemwhse_mst`) | "Warehouse is required"; must exist in that site [D9] |
| PartWhse `Company`, `PartNum`, `Plant`, `WarehouseCode` | default 55 (banner); header seen [D19] | `itemwhse_mst.item`, `whse` + site map | Use Add + Update together when the part's default warehouse already exists [D19] (2.4) |

## Map 3: customers. `custaddr_mst` to Customer / ShipTo

In SyteLine, `custaddr_mst` holds the customer's address at `cust_seq = 0` and its
ship-to addresses at `cust_seq > 0` (UNVERIFIED; non-address data sits in
`customer_mst`).

Load Customer before ShipTo (default 58, banner; parent-first rule [D23]).

| Kinetic | Cited? | From SyteLine (UNVERIFIED) | Notes |
|---------|--------|----------------------------|-------|
| Customer `Company` | [D24] (update set) | site map | Rule 1. A customer shared by two sites becomes two Customer rows, one per Company, if the sites map to different companies |
| Customer `CustID` | — | `custaddr_mst.cust_num` (cust_seq 0), trimmed | Rule 2 |
| Customer `CustNum` | — | **leave blank / let Kinetic assign** | Rule 2 |
| Customer `Name`, address | `Name` [D24] | `custaddr_mst.name`, address columns (cust_seq 0) | Customer Add required list is UNVERIFIED (question 52). Use the client's Template Builder |
| Customer `TerritoryID` | must match an existing code exactly [D18] | territory | `USA` worked, `U.S.A.` failed [D18] |
| ShipTo `Company`, `CustNumCustID`, `ShipToNum` | [D10][D11][D24] | site map; `cust_num` trimmed; `cust_seq` as text | `CustNumCustID` is required [D10][D11] |
| Default ShipTo | [D24] | cust_seq 0 address | Default ShipTo has a blank ShipToNum and cannot be updated through the ShipTo template; update it through the Customer template [D24] |

## Extract sketch (SyteLine side, read-only, on a copy)

Illustrative only. Table and column names are UNVERIFIED. `dbo.SiteMap` is your own
table (SyteLine site -> Kinetic Company, Plant).

```sql
-- OrderHed rows: CustID trimmed, CustNum deliberately not emitted (Rule 2)
SELECT m.Company,
       0                          AS OrderNum,        -- let Kinetic assign [D6][D7]
       LTRIM(RTRIM(co.cust_num))  AS CustomerCustID,  -- string -> CustID
       co.cust_po                 AS PONum,
       CONVERT(char(10), co.order_date, 23) AS OrderDate,
       co.co_num                  AS LegacyOrderNum   -- keep for cross-reference
FROM co_mst co
JOIN dbo.SiteMap m ON m.SiteRef = co.site_ref;        -- Rule 1: always join the site

-- OrderDtl: one row per (co_num, co_line); release rows go to OrderRel
SELECT m.Company, ci.co_num, ci.co_line, MIN(ci.item) AS PartNum, SUM(ci.qty_ordered) AS SellingQuantity
FROM coitem_mst ci
JOIN dbo.SiteMap m ON m.SiteRef = ci.site_ref
GROUP BY m.Company, ci.co_num, ci.co_line;
```

Then run the files through `dmt-validator/validate_dmt.py` before any load.

## What this document does not claim

- That the SyteLine names above are right for the client's version. None is cited.
- That any Kinetic column not marked as cited exists or is required.
- What DMT does with a row that breaks one of these rules.
