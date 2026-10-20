/* =============================================================================
   validation-queries.sql - SQL Server pre-check, equivalent to validate_dmt.py
   -----------------------------------------------------------------------------
   TEXT ONLY. Not run against any database in this kit. Run it on YOUR staging
   SQL Server, never on an Epicor database (and there is no direct SQL on
   multi-tenant cloud at all: 04-cloud-rules.md 1.1, [C2]).

   Setup assumed:
   - Schema [stg] holds one table per CSV, every column NVARCHAR(400), loaded
     as-is (no trimming), e.g. BULK INSERT ... WITH (FORMAT = 'CSV', FIRSTROW = 2).
   - Each table has an extra column RowNo INT = spreadsheet row (header = 1).
   - Columns named like CSV headers: stg.OrderDtl has [OrderRel#Plant] etc.
   - stg.Sites, stg.Uom and stg.LoadPlan hold reference/sites.csv,
     reference/uom.csv and load-plan.csv.

   Source IDs ([D#], [M#]) are in docs/reference/03-dmt.md and 02-baq.md.
   "lab check" = no cited source; a data-hygiene rule chosen for this kit.
   Rows tagged BANNER rest on an approved bucket A default:
   "Default chosen for the lab, not confirmed against Epicor."

   Two T-SQL traps this script avoids on purpose:
   1. '=' ignores trailing spaces (ANSI padding), so 'EA ' = 'EA' is TRUE.
      Whitespace is tested with DATALENGTH, not '=' or LEN().
   2. Default collations are usually case-insensitive. Plant/warehouse codes
      may be case-sensitive [D14], so site lookups use a _CS_ collation.
   ============================================================================= */

SET NOCOUNT ON;

IF OBJECT_ID('tempdb..#Finding') IS NOT NULL DROP TABLE #Finding;
CREATE TABLE #Finding (
    Severity   VARCHAR(10),
    CheckCode  VARCHAR(40),
    FileName   VARCHAR(40),
    RowNo      INT NULL,
    KeyText    NVARCHAR(400),
    ColumnName NVARCHAR(100),
    Value      NVARCHAR(400),
    Basis      NVARCHAR(400),
    Banner     BIT DEFAULT 0
);

/* Helper idea used throughout: a "clean" value strips spaces, tab, CR, LF.
   TRIM(... FROM ...) needs SQL Server 2017+. */

/* ---------------------------------------------------------------------------
   1. LOAD_ORDER (load-plan)
   --------------------------------------------------------------------------- */
;WITH r(Parent, Child, Basis, Banner) AS (
    SELECT 'Customer', 'ShipTo',    'approved lab default 58; [D23]; [D11]', 1 UNION ALL
    SELECT 'Part',     'PartPlant', 'cited source [D19]; [D20]',             0 UNION ALL
    SELECT 'Customer', 'OrderHed',  'approved lab default 59; [D8]',         1 UNION ALL
    SELECT 'Part',     'OrderDtl',  'approved lab default 59; [D8]',         1
)
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis, Banner)
SELECT 'ERROR', 'LOAD_ORDER', 'load-plan.csv', c.RowNo, r.Child, 'Seq', c.Seq,
       r.Child + ' planned at/before ' + r.Parent + '; ' + r.Basis, r.Banner
FROM r
JOIN stg.LoadPlan p ON p.Entity = r.Parent
JOIN stg.LoadPlan c ON c.Entity = r.Child
WHERE TRY_CONVERT(int, c.Seq) <= TRY_CONVERT(int, p.Seq);

/* ---------------------------------------------------------------------------
   2. REQUIRED_MISSING - blank values in columns a cited source shows as needed.
      Applied to Add and Update rows: required fields are enforced on update
      too [D15]. Missing COLUMNS are caught when the BULK INSERT format fails;
      check stg table definitions against the CSV header first.
   --------------------------------------------------------------------------- */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis, Banner)
SELECT 'ERROR', 'REQUIRED_MISSING', 'ShipTo.csv', RowNo, Company + '|' + ShipToNum, 'CustNumCustID', CustNumCustID,
       'required per cited source [D10][D11]', 0
FROM stg.ShipTo WHERE NULLIF(TRIM(CustNumCustID), '') IS NULL
UNION ALL
SELECT 'ERROR', 'REQUIRED_MISSING', 'Part.csv', RowNo, Company + '|' + PartNum, 'PartNum', PartNum,
       'required per cited source [D14]', 0
FROM stg.Part WHERE NULLIF(TRIM(PartNum), '') IS NULL
UNION ALL
SELECT 'ERROR', 'REQUIRED_MISSING', 'Part.csv', RowNo, Company + '|' + PartNum, 'PartDescription', PartDescription,
       'required per cited source [D14][D15]', 0
FROM stg.Part WHERE NULLIF(TRIM(PartDescription), '') IS NULL
UNION ALL
SELECT 'ERROR', 'REQUIRED_MISSING', 'PartPlant.csv', RowNo, Company + '|' + PartNum + '|' + Plant, 'PrimWhse', PrimWhse,
       'required per cited source [D9]', 0
FROM stg.PartPlant WHERE NULLIF(TRIM(PrimWhse), '') IS NULL
UNION ALL
SELECT 'ERROR', 'REQUIRED_MISSING', 'PartPlant.csv', RowNo, Company + '|' + PartNum + '|' + Plant, 'Company/PartNum/Plant', NULL,
       'required per cited source [D19] (approved lab default 54)', 1
FROM stg.PartPlant
WHERE NULLIF(TRIM(Company), '') IS NULL OR NULLIF(TRIM(PartNum), '') IS NULL OR NULLIF(TRIM(Plant), '') IS NULL
UNION ALL
SELECT 'ERROR', 'REQUIRED_MISSING', 'OrderHed.csv', RowNo, Company + '|' + OrderNum, 'CustomerCustID', CustomerCustID,
       'required per cited source [D8] (approved lab default 57)', 1
FROM stg.OrderHed WHERE NULLIF(TRIM(CustomerCustID), '') IS NULL;

/* Default ShipTo (blank ShipToNum) cannot be updated through ShipTo [D24]. */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'SHIPTO_DEFAULT_UPDATE', 'ShipTo.csv', RowNo, Company + '|' + CustNumCustID, 'ShipToNum', ShipToNum,
       'cited source [D24]'
FROM stg.ShipTo
WHERE TRIM(LabAction) = 'Update' AND NULLIF(TRIM(ShipToNum), '') IS NULL;

/* Warn only: approved default 53. */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis, Banner)
SELECT 'WARNING', 'OPTIONAL_MISSING', 'Part.csv', RowNo, Company + '|' + PartNum, 'TypeCode', TypeCode,
       'approved lab default 53 (warn, do not fail)', 1
FROM stg.Part WHERE NULLIF(TRIM(TypeCode), '') IS NULL;

/* ---------------------------------------------------------------------------
   3. WHITESPACE / hidden characters on key and code columns [D12].
      DATALENGTH counts trailing spaces; '=' and LEN() do not.
      Extend the column list to every column you load.
   --------------------------------------------------------------------------- */
;WITH v(FileName, RowNo, KeyText, ColumnName, Value) AS (
    SELECT 'Part.csv', RowNo, Company + '|' + PartNum, 'IUM',     IUM     FROM stg.Part UNION ALL
    SELECT 'Part.csv', RowNo, Company + '|' + PartNum, 'PUM',     PUM     FROM stg.Part UNION ALL
    SELECT 'Part.csv', RowNo, Company + '|' + PartNum, 'SalesUM', SalesUM FROM stg.Part UNION ALL
    SELECT 'Part.csv', RowNo, Company + '|' + PartNum, 'PartNum', PartNum FROM stg.Part UNION ALL
    SELECT 'Customer.csv', RowNo, Company + '|' + CustID, 'CustID', CustID FROM stg.Customer UNION ALL
    SELECT 'ShipTo.csv', RowNo, Company + '|' + CustNumCustID, 'CustNumCustID', CustNumCustID FROM stg.ShipTo UNION ALL
    SELECT 'PartPlant.csv', RowNo, Company + '|' + PartNum, 'Plant',    Plant    FROM stg.PartPlant UNION ALL
    SELECT 'PartPlant.csv', RowNo, Company + '|' + PartNum, 'PrimWhse', PrimWhse FROM stg.PartPlant UNION ALL
    SELECT 'OrderHed.csv', RowNo, Company + '|' + OrderNum, 'CustomerCustID', CustomerCustID FROM stg.OrderHed UNION ALL
    SELECT 'OrderDtl.csv', RowNo, Company + '|' + OrderNum + '|' + OrderLine, 'PartNum', PartNum FROM stg.OrderDtl UNION ALL
    SELECT 'OrderDtl.csv', RowNo, Company + '|' + OrderNum + '|' + OrderLine, 'OrderRel#Plant', [OrderRel#Plant] FROM stg.OrderDtl
)
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'WHITESPACE', FileName, RowNo, KeyText, ColumnName,
       REPLACE(REPLACE(REPLACE(Value, ' ', N'·'), CHAR(13), N'\r'), CHAR(10), N'\n'),
       'cited source [D12]: hidden characters cause lookup failures'
FROM v
WHERE Value IS NOT NULL
  AND (DATALENGTH(Value) <> DATALENGTH(TRIM(CHAR(32) + CHAR(9) + CHAR(10) + CHAR(13) FROM Value))
       OR Value LIKE N'%[' + CHAR(9) + CHAR(10) + CHAR(13) + N']%');

/* ---------------------------------------------------------------------------
   4. Types. TRY_CONVERT returns NULL instead of raising error 245 [M3].
      Never compare a staged NVARCHAR to an int column directly: int has higher
      precedence, the varchar side is converted, and 'LUMEN' fails [M2][M3].
   --------------------------------------------------------------------------- */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'CUSTNUM_NOT_INT', 'Customer.csv', RowNo, Company + '|' + CustID, 'CustNum', CustNum,
       'CustNum is the internal integer ID, CustID the string ID [D10]; [M2][M3]'
FROM stg.Customer
WHERE NULLIF(TRIM(CustNum), '') IS NOT NULL AND TRIM(CustNum) LIKE '%[^0-9-]%'
UNION ALL
SELECT 'ERROR', 'CUSTNUM_NOT_INT', 'OrderHed.csv', RowNo, Company + '|' + OrderNum, 'CustNum', CustNum,
       'CustNum is the internal integer ID, CustID the string ID [D10]; [M2][M3]'
FROM stg.OrderHed
WHERE NULLIF(TRIM(CustNum), '') IS NOT NULL AND TRIM(CustNum) LIKE '%[^0-9-]%'
UNION ALL
SELECT 'ERROR', 'TYPE_INT', 'OrderDtl.csv', RowNo, Company + '|' + OrderNum + '|' + OrderLine, 'OrderLine', OrderLine, 'lab check'
FROM stg.OrderDtl WHERE TRY_CONVERT(int, TRIM(OrderLine)) IS NULL
UNION ALL
SELECT 'ERROR', 'TYPE_INT', 'OrderHed.csv', RowNo, Company + '|' + OrderNum, 'OrderNum', OrderNum, 'lab check'
FROM stg.OrderHed WHERE TRY_CONVERT(int, TRIM(OrderNum)) IS NULL
UNION ALL
SELECT 'ERROR', 'TYPE_DECIMAL', 'OrderDtl.csv', RowNo, Company + '|' + OrderNum + '|' + OrderLine, 'SellingQuantity', SellingQuantity, 'lab check'
FROM stg.OrderDtl WHERE NULLIF(TRIM(SellingQuantity), '') IS NOT NULL AND TRY_CONVERT(decimal(18, 6), TRIM(SellingQuantity)) IS NULL;

/* BAD_DATE: batch format YYYY-MM-DD. Style 23 = yyyy-mm-dd. The LIKE pattern
   stops TRY_CONVERT from accepting other layouts. No cited DMT date format
   exists in the reference (lab check). */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'BAD_DATE', 'OrderHed.csv', h.RowNo, h.Company + '|' + h.OrderNum, d.ColumnName, d.Value, 'lab check'
FROM stg.OrderHed h
CROSS APPLY (VALUES ('OrderDate', h.OrderDate), ('RequestDate', h.RequestDate), ('NeedByDate', h.NeedByDate)) d(ColumnName, Value)
WHERE NULLIF(TRIM(d.Value), '') IS NOT NULL
  AND (TRIM(d.Value) NOT LIKE '[12][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9]'
       OR TRY_CONVERT(date, TRIM(d.Value), 23) IS NULL);

/* ---------------------------------------------------------------------------
   5. DUPLICATE_KEY - one finding per extra row (first row kept).
   --------------------------------------------------------------------------- */
;WITH k AS (
    SELECT 'Customer.csv' AS FileName, RowNo, TRIM(Company) + '|' + TRIM(CustID) AS KeyText,
           'lab check: lab key (Company, CustID)' AS Basis, 0 AS Banner FROM stg.Customer
    UNION ALL SELECT 'ShipTo.csv', RowNo, TRIM(Company) + '|' + TRIM(CustNumCustID) + '|' + TRIM(ShipToNum),
           'lab check: lab key', 0 FROM stg.ShipTo
    UNION ALL SELECT 'Part.csv', RowNo, TRIM(Company) + '|' + TRIM(PartNum), 'lab check: lab key', 0 FROM stg.Part
    UNION ALL SELECT 'PartPlant.csv', RowNo, TRIM(Company) + '|' + TRIM(PartNum) + '|' + TRIM(Plant),
           'approved lab default 54', 1 FROM stg.PartPlant
    UNION ALL SELECT 'OrderHed.csv', RowNo, TRIM(Company) + '|' + TRIM(OrderNum), 'lab check: lab key', 0 FROM stg.OrderHed
    UNION ALL SELECT 'OrderDtl.csv', RowNo, TRIM(Company) + '|' + TRIM(OrderNum) + '|' + TRIM(OrderLine),
           'cited source [D6]: distinct OrderLine per order', 0 FROM stg.OrderDtl
), n AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY FileName, KeyText ORDER BY RowNo) AS rn FROM k
)
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis, Banner)
SELECT 'ERROR', 'DUPLICATE_KEY', FileName, RowNo, KeyText, 'key', KeyText, Basis, Banner
FROM n WHERE rn > 1;

/* ---------------------------------------------------------------------------
   6. UPDATE_KEY_CHANGE - Update finds the record by its primary key [D21].
      LabTargetKey is the lab's pipe-separated key of the record being updated.
   --------------------------------------------------------------------------- */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'UPDATE_KEY_CHANGE', 'Customer.csv', RowNo, TRIM(Company) + '|' + TRIM(CustID), 'CustID',
       'target ' + LabTargetKey, 'cited source [D21]'
FROM stg.Customer
WHERE TRIM(LabAction) = 'Update' AND NULLIF(TRIM(LabTargetKey), '') IS NOT NULL
  AND TRIM(Company) + '|' + TRIM(CustID) COLLATE Latin1_General_CS_AS <> TRIM(LabTargetKey) COLLATE Latin1_General_CS_AS
UNION ALL
SELECT 'ERROR', 'UPDATE_KEY_CHANGE', 'Part.csv', RowNo, TRIM(Company) + '|' + TRIM(PartNum), 'PartNum',
       'target ' + LabTargetKey, 'cited source [D21]'
FROM stg.Part
WHERE TRIM(LabAction) = 'Update' AND NULLIF(TRIM(LabTargetKey), '') IS NOT NULL
  AND TRIM(Company) + '|' + TRIM(PartNum) COLLATE Latin1_General_CS_AS <> TRIM(LabTargetKey) COLLATE Latin1_General_CS_AS;
/* Repeat for ShipTo, PartPlant, OrderHed, OrderDtl if they carry Update rows. */

/* ---------------------------------------------------------------------------
   7. Cross-file keys. Parent set = rows in the batch + records targeted by
      Update rows (they already exist in the target). Always join on Company:
      the same CustID / PartNum exists in MFG01 and MFG02 (02-baq defect 1).
   --------------------------------------------------------------------------- */
IF OBJECT_ID('tempdb..#CustKey') IS NOT NULL DROP TABLE #CustKey;
SELECT DISTINCT TRIM(Company) AS Company, TRIM(CustID) AS CustID INTO #CustKey FROM stg.Customer
UNION SELECT TRIM(LEFT(LabTargetKey, CHARINDEX('|', LabTargetKey) - 1)),
             TRIM(SUBSTRING(LabTargetKey, CHARINDEX('|', LabTargetKey) + 1, 400))
FROM stg.Customer WHERE TRIM(LabAction) = 'Update' AND CHARINDEX('|', LabTargetKey) > 0;

IF OBJECT_ID('tempdb..#PartKey') IS NOT NULL DROP TABLE #PartKey;
SELECT DISTINCT TRIM(Company) AS Company, TRIM(PartNum) AS PartNum INTO #PartKey FROM stg.Part
UNION SELECT TRIM(LEFT(LabTargetKey, CHARINDEX('|', LabTargetKey) - 1)),
             TRIM(SUBSTRING(LabTargetKey, CHARINDEX('|', LabTargetKey) + 1, 400))
FROM stg.Part WHERE TRIM(LabAction) = 'Update' AND CHARINDEX('|', LabTargetKey) > 0;

INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis, Banner)
SELECT 'ERROR', 'FK_CUSTOMER', 'ShipTo.csv', s.RowNo, s.Company + '|' + s.ShipToNum, 'CustNumCustID', s.CustNumCustID,
       'approved lab default 58; [D11]', 1
FROM stg.ShipTo s
WHERE NULLIF(TRIM(s.CustNumCustID), '') IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM #CustKey c WHERE c.Company = TRIM(s.Company) AND c.CustID = TRIM(s.CustNumCustID))
UNION ALL
SELECT 'ERROR', 'FK_CUSTOMER', 'OrderHed.csv', h.RowNo, h.Company + '|' + h.OrderNum, 'CustomerCustID', h.CustomerCustID,
       'approved lab default 59; [D8]', 1
FROM stg.OrderHed h
WHERE NULLIF(TRIM(h.CustomerCustID), '') IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM #CustKey c WHERE c.Company = TRIM(h.Company) AND c.CustID = TRIM(h.CustomerCustID))
UNION ALL
SELECT 'ERROR', 'FK_PART', 'PartPlant.csv', p.RowNo, p.Company + '|' + p.PartNum + '|' + p.Plant, 'PartNum', p.PartNum,
       'cited source [D19]', 0
FROM stg.PartPlant p
WHERE NULLIF(TRIM(p.PartNum), '') IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM #PartKey k WHERE k.Company = TRIM(p.Company) AND k.PartNum = TRIM(p.PartNum))
UNION ALL
SELECT 'ERROR', 'FK_PART', 'OrderDtl.csv', d.RowNo, d.Company + '|' + d.OrderNum + '|' + d.OrderLine, 'PartNum', d.PartNum,
       'approved lab default 59; [D8]', 1
FROM stg.OrderDtl d
WHERE NULLIF(TRIM(d.PartNum), '') IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM #PartKey k WHERE k.Company = TRIM(d.Company) AND k.PartNum = TRIM(d.PartNum))
UNION ALL
SELECT 'ERROR', 'FK_ORDERHED', 'OrderDtl.csv', d.RowNo, d.Company + '|' + d.OrderNum + '|' + d.OrderLine, 'OrderNum', d.OrderNum,
       'lab check', 0
FROM stg.OrderDtl d
WHERE NOT EXISTS (SELECT 1 FROM stg.OrderHed h WHERE TRIM(h.Company) = TRIM(d.Company) AND TRIM(h.OrderNum) = TRIM(d.OrderNum));

/* CustNum on the order must match the customer's CustNum in the SAME Company.
   Compare as int only after TRY_CONVERT on both sides (defect 2). */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'CUSTNUM_MISMATCH', 'OrderHed.csv', h.RowNo, h.Company + '|' + h.OrderNum, 'CustNum', h.CustNum,
       'lab check; [D10]'
FROM stg.OrderHed h
JOIN stg.Customer c
  ON TRIM(c.Company) = TRIM(h.Company) AND TRIM(c.CustID) = TRIM(h.CustomerCustID)
WHERE TRY_CONVERT(int, TRIM(h.CustNum)) IS NOT NULL
  AND TRY_CONVERT(int, TRIM(c.CustNum)) IS NOT NULL
  AND TRY_CONVERT(int, TRIM(h.CustNum)) <> TRY_CONVERT(int, TRIM(c.CustNum));

/* UOM codes must exist in the target UOM class [D13]. */
;WITH u(RowNo, Company, PartNum, ColumnName, Value) AS (
    SELECT RowNo, Company, PartNum, 'IUM', IUM FROM stg.Part UNION ALL
    SELECT RowNo, Company, PartNum, 'PUM', PUM FROM stg.Part UNION ALL
    SELECT RowNo, Company, PartNum, 'SalesUM', SalesUM FROM stg.Part
)
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'UOM_NOT_FOUND', 'Part.csv', u.RowNo, u.Company + '|' + u.PartNum, u.ColumnName, u.Value, 'cited source [D13]'
FROM u
WHERE NULLIF(TRIM(u.Value), '') IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM stg.Uom x
                  WHERE TRIM(x.Company) = TRIM(u.Company)
                    AND TRIM(x.UOMCode) COLLATE Latin1_General_CS_AS = TRIM(u.Value) COLLATE Latin1_General_CS_AS);

/* ---------------------------------------------------------------------------
   8. Site mapping. Case-sensitive on purpose [D14].
   --------------------------------------------------------------------------- */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'SITE_UNKNOWN', 'PartPlant.csv', p.RowNo, p.Company + '|' + p.PartNum, 'Plant', p.Plant, '[D19]; [D14]'
FROM stg.PartPlant p
WHERE NULLIF(TRIM(p.Plant), '') IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM stg.Sites s WHERE TRIM(s.Company) = TRIM(p.Company)
                  AND TRIM(s.Plant) COLLATE Latin1_General_CS_AS = TRIM(p.Plant) COLLATE Latin1_General_CS_AS)
UNION ALL
SELECT 'ERROR', 'WHSE_NOT_IN_SITE', 'PartPlant.csv', p.RowNo, p.Company + '|' + p.PartNum + '|' + p.Plant, 'PrimWhse', p.PrimWhse,
       'cited source [D9]'
FROM stg.PartPlant p
WHERE NULLIF(TRIM(p.PrimWhse), '') IS NOT NULL
  AND EXISTS (SELECT 1 FROM stg.Sites s WHERE TRIM(s.Company) = TRIM(p.Company)
              AND TRIM(s.Plant) COLLATE Latin1_General_CS_AS = TRIM(p.Plant) COLLATE Latin1_General_CS_AS)
  AND NOT EXISTS (SELECT 1 FROM stg.Sites s WHERE TRIM(s.Company) = TRIM(p.Company)
                  AND TRIM(s.Plant) COLLATE Latin1_General_CS_AS = TRIM(p.Plant) COLLATE Latin1_General_CS_AS
                  AND TRIM(s.WarehouseCode) COLLATE Latin1_General_CS_AS = TRIM(p.PrimWhse) COLLATE Latin1_General_CS_AS)
UNION ALL
SELECT 'ERROR', 'SITE_UNKNOWN', 'OrderDtl.csv', d.RowNo, d.Company + '|' + d.OrderNum + '|' + d.OrderLine, 'OrderRel#Plant',
       d.[OrderRel#Plant], 'lab check; [D14]'
FROM stg.OrderDtl d
WHERE NULLIF(TRIM(d.[OrderRel#Plant]), '') IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM stg.Sites s WHERE TRIM(s.Company) = TRIM(d.Company)
                  AND TRIM(s.Plant) COLLATE Latin1_General_CS_AS = TRIM(d.[OrderRel#Plant]) COLLATE Latin1_General_CS_AS);

/* PARTPLANT_MISSING_FOR_SITE: the line's part exists, the site exists, but no
   PartPlant row for (Company, PartNum, site). Lab check / data gap: no cited
   source states what happens to such a line. Joining on Company is the point:
   a PartPlant row in MFG01 does not cover an MFG02 line. */
INSERT #Finding (Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis)
SELECT 'ERROR', 'PARTPLANT_MISSING_FOR_SITE', 'OrderDtl.csv', d.RowNo,
       d.Company + '|' + d.OrderNum + '|' + d.OrderLine, 'PartNum, OrderRel#Plant',
       d.PartNum + ' @ ' + d.[OrderRel#Plant],
       'lab check (data gap); PrimWhse per site [D9]; Part then PartPlant [D19][D20]'
FROM stg.OrderDtl d
WHERE EXISTS (SELECT 1 FROM #PartKey k WHERE k.Company = TRIM(d.Company) AND k.PartNum = TRIM(d.PartNum))
  AND EXISTS (SELECT 1 FROM stg.Sites s WHERE TRIM(s.Company) = TRIM(d.Company)
              AND TRIM(s.Plant) COLLATE Latin1_General_CS_AS = TRIM(d.[OrderRel#Plant]) COLLATE Latin1_General_CS_AS)
  AND NOT EXISTS (SELECT 1 FROM stg.PartPlant p
                  WHERE TRIM(p.Company) = TRIM(d.Company)
                    AND TRIM(p.PartNum) = TRIM(d.PartNum)
                    AND TRIM(p.Plant) COLLATE Latin1_General_CS_AS = TRIM(d.[OrderRel#Plant]) COLLATE Latin1_General_CS_AS);

/* ---------------------------------------------------------------------------
   Remediation list
   --------------------------------------------------------------------------- */
SELECT Severity, CheckCode, FileName, RowNo, KeyText, ColumnName, Value, Basis,
       CASE WHEN Banner = 1 THEN 'Default chosen for the lab, not confirmed against Epicor.' ELSE '' END AS Banner
FROM #Finding
ORDER BY CASE Severity WHEN 'ERROR' THEN 0 ELSE 1 END, FileName, RowNo, CheckCode;

SELECT Severity, CheckCode, COUNT(*) AS Findings
FROM #Finding GROUP BY Severity, CheckCode ORDER BY Severity, CheckCode;
