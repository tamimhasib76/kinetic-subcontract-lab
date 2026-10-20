/* =============================================================================
   sql/02-erp-rpt-staging.sql
   -----------------------------------------------------------------------------
   Epicor SSRS Report Staging Database & Stored Procedure
   Target: Microsoft SQL Server 2016+
   Database: [ErpReporting]
   Schema:   [dbo]

   Objects created:
   - dbo.StagedReportRun     (audit & lifecycle tracking table for staged GUID sets)
   - dbo.usp_StageEpicorReport (stored procedure that materializes per-run <Table>_<GUID> tables
                                using dynamic column lists from dbo.RddColumn WHERE Exclude = 0)

   Prerequisites:
   - Run sql/01-erp-app-schema.sql first (creates [ErpLab]).
   - Run sql/03-rdd-definitions.sql before executing dbo.usp_StageEpicorReport
     (creates dbo.RddTable, dbo.RddColumn, dbo.RddRelationship, and dbo.usp_SetRddExclude).

   Supported @ReportType values:
   - 'PackSlip'   (@Key1 = PackNum)
   - 'OrderAck'   (@Key1 = OrderNum)
   - 'ARForm'     (@Key1 = InvoiceNum)
   - 'OpenOrders' (@Key1 = NULL or optional filter; stages BAQReportResult_<GUID>
                   for all open orders in @Company)
   ============================================================================= */

SET NOCOUNT ON;

-- Ensure database [ErpReporting] exists
IF DB_ID('ErpReporting') IS NULL
BEGIN
    CREATE DATABASE [ErpReporting];
END;
GO

USE [ErpReporting];
GO

/* =============================================================================
   1. STAGING RUN TRACKING TABLE
   ============================================================================= */

IF OBJECT_ID('dbo.StagedReportRun', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.StagedReportRun (
        RunID           INT IDENTITY(1,1) NOT NULL,
        TableGuid       NVARCHAR(36)      NOT NULL,
        ReportType      NVARCHAR(30)      NOT NULL,
        Company         NVARCHAR(8)       NOT NULL,
        Key1            NVARCHAR(50)      NULL,
        StagedAtUtc     DATETIME2(3)      NOT NULL DEFAULT SYSUTCDATETIME(),
        StagedTables    NVARCHAR(500)     NOT NULL,
        CONSTRAINT PK_StagedReportRun PRIMARY KEY CLUSTERED (RunID),
        CONSTRAINT UQ_StagedReportRun_TableGuid UNIQUE (TableGuid)
    );
END;
GO

/* =============================================================================
   2. STORED PROCEDURE: dbo.usp_StageEpicorReport
   ============================================================================= */

IF OBJECT_ID('dbo.usp_StageEpicorReport', 'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_StageEpicorReport;
GO

CREATE PROCEDURE dbo.usp_StageEpicorReport
    @ReportType NVARCHAR(30),
    @Company    NVARCHAR(8),
    @Key1       NVARCHAR(50) = NULL,
    @TableGuid  NVARCHAR(36) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- Verify RDD metadata tables exist (created by sql/03-rdd-definitions.sql)
    IF OBJECT_ID('dbo.RddColumn', 'U') IS NULL
    BEGIN
        RAISERROR('RDD metadata table dbo.RddColumn does not exist. Run sql/03-rdd-definitions.sql before calling dbo.usp_StageEpicorReport.', 16, 1);
        RETURN;
    END;

    -- Validate @ReportType
    IF @ReportType NOT IN (N'PackSlip', N'OrderAck', N'ARForm', N'OpenOrders')
    BEGIN
        RAISERROR('Unsupported @ReportType "%s". Supported values: PackSlip, OrderAck, ARForm, OpenOrders.', 16, 1, @ReportType);
        RETURN;
    END;

    -- Validate @Company exists in ErpLab.Erp.Company
    IF NOT EXISTS (SELECT 1 FROM ErpLab.Erp.Company WHERE Company = @Company)
    BEGIN
        RAISERROR('Company "%s" does not exist in ErpLab.Erp.Company.', 16, 1, @Company);
        RETURN;
    END;

    -- Validate @Key1 for transactional document reports
    DECLARE @Key1Int INT = NULL;
    IF @ReportType IN (N'PackSlip', N'OrderAck', N'ARForm')
    BEGIN
        IF @Key1 IS NULL OR LTRIM(RTRIM(@Key1)) = N''
        BEGIN
            RAISERROR('@Key1 is required when @ReportType is "%s".', 16, 1, @ReportType);
            RETURN;
        END;

        SET @Key1Int = TRY_CAST(@Key1 AS INT);
        IF @Key1Int IS NULL
        BEGIN
            RAISERROR('@Key1 value "%s" is not a valid integer document number for @ReportType "%s".', 16, 1, @Key1, @ReportType);
            RETURN;
        END;
    END;

    -- Generate or sanitize 32-character lowercase hexadecimal GUID suffix (no hyphens)
    DECLARE @GuidSuffix NVARCHAR(32);
    IF @TableGuid IS NOT NULL AND LEN(REPLACE(LTRIM(RTRIM(@TableGuid)), N'-', N'')) = 32
        SET @GuidSuffix = LOWER(REPLACE(LTRIM(RTRIM(@TableGuid)), N'-', N''));
    ELSE
        SET @GuidSuffix = LOWER(REPLACE(CONVERT(NVARCHAR(36), NEWID()), N'-', N''));

    -- Validate strictly hexadecimal characters [0-9a-f] to keep dynamic table names safe
    IF @GuidSuffix LIKE N'%[^0-9a-f]%'
    BEGIN
        RAISERROR('Invalid @TableGuid format. Must contain only hexadecimal characters.', 16, 1);
        RETURN;
    END;

    SET @TableGuid = @GuidSuffix;

    DECLARE @Sql NVARCHAR(MAX);
    DECLARE @StagedTablesList NVARCHAR(500) = N'';
    DECLARE @ColsRptLabels NVARCHAR(MAX);
    DECLARE @ColsCompany NVARCHAR(MAX);
    DECLARE @ColsCustomer NVARCHAR(MAX);
    DECLARE @ColsShipTo NVARCHAR(MAX);

    /* =========================================================================
       BRANCH 1: PackSlip (@Key1 = PackNum)
       Staged tables (columns built dynamically from dbo.RddColumn WHERE Exclude = 0):
         - dbo.[RptLabels_<GUID>]
         - dbo.[Company_<GUID>]
         - dbo.[ShipHead_<GUID>]  (Weight is Exclude = 1 in base RDD; un-excluded in Lab R6 D4)
         - dbo.[ShipDtl_<GUID>]   (CustPartNum and linked OrderNum_ProjManager_c are Exclude = 1
                                   in base RDD; un-excluded in Labs R1 and R2)
         - dbo.[Customer_<GUID>]
         - dbo.[ShipTo_<GUID>]
       ========================================================================= */
    IF @ReportType = N'PackSlip'
    BEGIN
        DECLARE @ColsShipHead NVARCHAR(MAX);
        DECLARE @ColsShipDtl  NVARCHAR(MAX);

        SELECT @ColsRptLabels = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'PackSlip' AND TableName = N'RptLabels' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsCompany = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'PackSlip' AND TableName = N'Company' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsShipHead = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'PackSlip' AND TableName = N'ShipHead' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsShipDtl = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'PackSlip' AND TableName = N'ShipDtl' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsCustomer = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'PackSlip' AND TableName = N'Customer' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsShipTo = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'PackSlip' AND TableName = N'ShipTo' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SET @Sql = N'
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'Company_'   + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'Company_'   + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'ShipHead_'  + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'ShipHead_'  + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'ShipDtl_'   + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'ShipDtl_'   + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'Customer_'  + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'Customer_'  + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'ShipTo_'    + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'ShipTo_'    + @GuidSuffix) + N';

        SELECT ' + @ColsRptLabels + N'
        INTO dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N'
        FROM (
            SELECT
                CAST(N''ENU''             AS NVARCHAR(10))  AS [RptLanguageID],
                CAST(N''PACKING SLIP''    AS NVARCHAR(100)) AS [LblPackSlipTitle],
                CAST(N''Pack Number:''    AS NVARCHAR(50))  AS [LblPackNum],
                CAST(N''Ship Date:''      AS NVARCHAR(50))  AS [LblShipDate],
                CAST(N''Customer:''       AS NVARCHAR(50))  AS [LblCustNum],
                CAST(N''Tracking #:''     AS NVARCHAR(50))  AS [LblTrackingNumber],
                CAST(N''Part Number''     AS NVARCHAR(50))  AS [LblPartNum],
                CAST(N''Description''     AS NVARCHAR(50))  AS [LblLineDesc],
                CAST(N''Cust Part #''     AS NVARCHAR(50))  AS [LblCustPartNum],
                CAST(N''Shipped Qty''     AS NVARCHAR(50))  AS [LblShipQty],
                CAST(N''Project Manager'' AS NVARCHAR(50))  AS [LblProjManager]
        ) AS src;

        SELECT ' + @ColsCompany + N'
        INTO dbo.' + QUOTENAME(N'Company_' + @GuidSuffix) + N'
        FROM ErpLab.Erp.Company AS src
        WHERE src.Company = @pCompany;

        SELECT ' + @ColsShipHead + N'
        INTO dbo.' + QUOTENAME(N'ShipHead_' + @GuidSuffix) + N'
        FROM ErpLab.Erp.ShipHead AS src
        WHERE src.Company = @pCompany
          AND src.PackNum = @pKey1Int;

        SELECT ' + @ColsShipDtl + N'
        INTO dbo.' + QUOTENAME(N'ShipDtl_' + @GuidSuffix) + N'
        FROM (
            SELECT
                d.[Company],
                d.[PackNum],
                d.[PackLine],
                d.[OrderNum],
                d.[OrderLine],
                d.[OrderRelNum],
                d.[PartNum],
                d.[LineDesc],
                d.[OurInventoryShipQty],
                d.[SellingShippedQty],
                d.[Packages],
                d.[IUM],
                d.[SalesUM],
                d.[CustPartNum],
                d.[HeatNumber_c],
                d.[CertificateOfConformance_c],
                oh.[ProjManager_c] AS [OrderNum_ProjManager_c]
            FROM ErpLab.Erp.ShipDtl d
            LEFT JOIN ErpLab.Erp.OrderHed oh
                ON oh.Company = d.Company
               AND oh.OrderNum = d.OrderNum
            WHERE d.Company = @pCompany
              AND d.PackNum = @pKey1Int
        ) AS src;

        SELECT ' + @ColsCustomer + N'
        INTO dbo.' + QUOTENAME(N'Customer_' + @GuidSuffix) + N'
        FROM (
            SELECT DISTINCT c.*
            FROM ErpLab.Erp.Customer c
            INNER JOIN ErpLab.Erp.ShipHead h
                ON h.Company = c.Company
               AND h.CustNum = c.CustNum
            WHERE h.Company = @pCompany
              AND h.PackNum = @pKey1Int
        ) AS src;

        SELECT ' + @ColsShipTo + N'
        INTO dbo.' + QUOTENAME(N'ShipTo_' + @GuidSuffix) + N'
        FROM (
            SELECT DISTINCT st.*
            FROM ErpLab.Erp.ShipTo st
            INNER JOIN ErpLab.Erp.ShipHead h
                ON h.Company = st.Company
               AND ISNULL(h.ShipToCustNum, h.CustNum) = st.CustNum
               AND h.ShipToNum = st.ShipToNum
            WHERE h.Company = @pCompany
              AND h.PackNum = @pKey1Int
        ) AS src;
        ';

        EXEC sp_executesql
            @stmt = @Sql,
            @params = N'@pCompany NVARCHAR(8), @pKey1Int INT',
            @pCompany = @Company,
            @pKey1Int = @Key1Int;

        SET @StagedTablesList = N'RptLabels_' + @GuidSuffix + N',Company_' + @GuidSuffix + N',ShipHead_' + @GuidSuffix + N',ShipDtl_' + @GuidSuffix + N',Customer_' + @GuidSuffix + N',ShipTo_' + @GuidSuffix;
    END

    /* =========================================================================
       BRANCH 2: OrderAck (@Key1 = OrderNum)
       Staged tables (columns built dynamically from dbo.RddColumn WHERE Exclude = 0):
         - dbo.[RptLabels_<GUID>]
         - dbo.[Company_<GUID>]
         - dbo.[OrderHed_<GUID>]
         - dbo.[OrderDtl_<GUID>]  (RevisionNum and ExtWeight are Exclude = 1 in base RDD;
                                   un-excluded in Lab R3; linked PartNum_SteelGauge_c and
                                   PartNum_PPAP_c included)
         - dbo.[OrderRel_<GUID>]  (includes RelHoldReason_c)
         - dbo.[Customer_<GUID>]
       ========================================================================= */
    ELSE IF @ReportType = N'OrderAck'
    BEGIN
        DECLARE @ColsOrderHed NVARCHAR(MAX);
        DECLARE @ColsOrderDtl NVARCHAR(MAX);
        DECLARE @ColsOrderRel NVARCHAR(MAX);

        SELECT @ColsRptLabels = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'OrderAck' AND TableName = N'RptLabels' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsCompany = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'OrderAck' AND TableName = N'Company' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsOrderHed = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'OrderAck' AND TableName = N'OrderHed' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsOrderDtl = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'OrderAck' AND TableName = N'OrderDtl' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsOrderRel = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'OrderAck' AND TableName = N'OrderRel' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsCustomer = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'OrderAck' AND TableName = N'Customer' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SET @Sql = N'
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'Company_'   + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'Company_'   + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'OrderHed_'  + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'OrderHed_'  + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'OrderDtl_'  + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'OrderDtl_'  + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'OrderRel_'  + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'OrderRel_'  + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'Customer_'  + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'Customer_'  + @GuidSuffix) + N';

        SELECT ' + @ColsRptLabels + N'
        INTO dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N'
        FROM (
            SELECT
                CAST(N''ENU''                  AS NVARCHAR(10))  AS [RptLanguageID],
                CAST(N''ORDER ACKNOWLEDGMENT'' AS NVARCHAR(100)) AS [LblOrderAckTitle],
                CAST(N''Order Number:''        AS NVARCHAR(50))  AS [LblOrderNum],
                CAST(N''Order Date:''          AS NVARCHAR(50))  AS [LblOrderDate],
                CAST(N''Customer PO:''         AS NVARCHAR(50))  AS [LblPONum],
                CAST(N''Need By Date:''        AS NVARCHAR(50))  AS [LblNeedByDate],
                CAST(N''Part Number''          AS NVARCHAR(50))  AS [LblPartNum],
                CAST(N''Rev''                  AS NVARCHAR(50))  AS [LblRevisionNum],
                CAST(N''Description''          AS NVARCHAR(50))  AS [LblLineDesc],
                CAST(N''Order Qty''            AS NVARCHAR(50))  AS [LblOrderQty],
                CAST(N''Unit Price''           AS NVARCHAR(50))  AS [LblUnitPrice],
                CAST(N''Ext Weight''           AS NVARCHAR(50))  AS [LblExtWeight],
                CAST(N''Rel #''                AS NVARCHAR(50))  AS [LblRelNum]
        ) AS src;

        SELECT ' + @ColsCompany + N'
        INTO dbo.' + QUOTENAME(N'Company_' + @GuidSuffix) + N'
        FROM ErpLab.Erp.Company AS src
        WHERE src.Company = @pCompany;

        SELECT ' + @ColsOrderHed + N'
        INTO dbo.' + QUOTENAME(N'OrderHed_' + @GuidSuffix) + N'
        FROM ErpLab.Erp.OrderHed AS src
        WHERE src.Company = @pCompany
          AND src.OrderNum = @pKey1Int;

        SELECT ' + @ColsOrderDtl + N'
        INTO dbo.' + QUOTENAME(N'OrderDtl_' + @GuidSuffix) + N'
        FROM (
            SELECT
                d.[Company],
                d.[OrderNum],
                d.[OrderLine],
                d.[PartNum],
                d.[LineDesc],
                d.[OrderQty],
                d.[SellingQuantity],
                d.[SalesUM],
                d.[UnitPrice],
                d.[DocUnitPrice],
                d.[DspUnitPrice],
                d.[OpenLine],
                d.[VoidLine],
                d.[NeedByDate],
                d.[RequestDate],
                d.[RevisionNum],
                d.[ExtWeight],
                d.[FabricationNotes_c],
                p.[SteelGauge_c] AS [PartNum_SteelGauge_c],
                p.[PPAP_c]       AS [PartNum_PPAP_c]
            FROM ErpLab.Erp.OrderDtl d
            LEFT JOIN ErpLab.Erp.Part p
                ON p.Company = d.Company
               AND p.PartNum = d.PartNum
            WHERE d.Company = @pCompany
              AND d.OrderNum = @pKey1Int
        ) AS src;

        SELECT ' + @ColsOrderRel + N'
        INTO dbo.' + QUOTENAME(N'OrderRel_' + @GuidSuffix) + N'
        FROM ErpLab.Erp.OrderRel AS src
        WHERE src.Company = @pCompany
          AND src.OrderNum = @pKey1Int;

        SELECT ' + @ColsCustomer + N'
        INTO dbo.' + QUOTENAME(N'Customer_' + @GuidSuffix) + N'
        FROM (
            SELECT DISTINCT c.*
            FROM ErpLab.Erp.Customer c
            INNER JOIN ErpLab.Erp.OrderHed h
                ON h.Company = c.Company
               AND h.CustNum = c.CustNum
            WHERE h.Company = @pCompany
              AND h.OrderNum = @pKey1Int
        ) AS src;
        ';

        EXEC sp_executesql
            @stmt = @Sql,
            @params = N'@pCompany NVARCHAR(8), @pKey1Int INT',
            @pCompany = @Company,
            @pKey1Int = @Key1Int;

        SET @StagedTablesList = N'RptLabels_' + @GuidSuffix + N',Company_' + @GuidSuffix + N',OrderHed_' + @GuidSuffix + N',OrderDtl_' + @GuidSuffix + N',OrderRel_' + @GuidSuffix + N',Customer_' + @GuidSuffix;
    END

    /* =========================================================================
       BRANCH 3: ARForm (@Key1 = InvoiceNum)
       Staged tables (columns built dynamically from dbo.RddColumn WHERE Exclude = 0):
         - dbo.[RptLabels_<GUID>]
         - dbo.[Company_<GUID>]
         - dbo.[InvcHead_<GUID>]  (Base columns: Company, InvoiceNum, CustNum, InvoiceDate,
                                   OrderNum, InvoiceType, InvoiceAmt, TermsCode, OpenInvoice,
                                   RptLanguageID, BillingContact_c; RemitToName, RemitToAddress1,
                                   RemitToCity, RemitToState, RemitToZip, and ShipToPONum_c are
                                   Exclude = 1 in base RDD and un-excluded in Lab R4)
         - dbo.[InvcDtl_<GUID>]
         - dbo.[Customer_<GUID>]
         - dbo.[ShipTo_<GUID>]    (joined from InvcDtl on Company, ShipToCustNum -> CustNum,
                                   ShipToNum per InvcDtlShipTo relationship added in Lab R4)
       ========================================================================= */
    ELSE IF @ReportType = N'ARForm'
    BEGIN
        DECLARE @ColsInvcHead NVARCHAR(MAX);
        DECLARE @ColsInvcDtl  NVARCHAR(MAX);

        SELECT @ColsRptLabels = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'ARForm' AND TableName = N'RptLabels' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsCompany = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'ARForm' AND TableName = N'Company' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsInvcHead = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'ARForm' AND TableName = N'InvcHead' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsInvcDtl = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'ARForm' AND TableName = N'InvcDtl' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsCustomer = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'ARForm' AND TableName = N'Customer' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsShipTo = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'ARForm' AND TableName = N'ShipTo' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SET @Sql = N'
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'Company_'   + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'Company_'   + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'InvcHead_'  + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'InvcHead_'  + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'InvcDtl_'   + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'InvcDtl_'   + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'Customer_'  + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'Customer_'  + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'ShipTo_'    + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'ShipTo_'    + @GuidSuffix) + N';

        SELECT ' + @ColsRptLabels + N'
        INTO dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N'
        FROM (
            SELECT
                CAST(N''ENU''             AS NVARCHAR(10))  AS [RptLanguageID],
                CAST(N''INVOICE''         AS NVARCHAR(100)) AS [LblInvoiceTitle],
                CAST(N''Invoice Number:'' AS NVARCHAR(50))  AS [LblInvoiceNum],
                CAST(N''Invoice Date:''   AS NVARCHAR(50))  AS [LblInvoiceDate],
                CAST(N''Sales Order:''    AS NVARCHAR(50))  AS [LblOrderNum],
                CAST(N''Terms:''          AS NVARCHAR(50))  AS [LblTermsCode],
                CAST(N''Remit To:''       AS NVARCHAR(50))  AS [LblRemitTo],
                CAST(N''Ship-To PO #:''   AS NVARCHAR(50))  AS [LblShipToPO],
                CAST(N''Part Number''     AS NVARCHAR(50))  AS [LblPartNum],
                CAST(N''Description''     AS NVARCHAR(50))  AS [LblLineDesc],
                CAST(N''Shipped Qty''     AS NVARCHAR(50))  AS [LblShipQty],
                CAST(N''Unit Price''      AS NVARCHAR(50))  AS [LblUnitPrice],
                CAST(N''Extended Price''  AS NVARCHAR(50))  AS [LblExtPrice]
        ) AS src;

        SELECT ' + @ColsCompany + N'
        INTO dbo.' + QUOTENAME(N'Company_' + @GuidSuffix) + N'
        FROM ErpLab.Erp.Company AS src
        WHERE src.Company = @pCompany;

        SELECT ' + @ColsInvcHead + N'
        INTO dbo.' + QUOTENAME(N'InvcHead_' + @GuidSuffix) + N'
        FROM ErpLab.Erp.InvcHead AS src
        WHERE src.Company = @pCompany
          AND src.InvoiceNum = @pKey1Int;

        SELECT ' + @ColsInvcDtl + N'
        INTO dbo.' + QUOTENAME(N'InvcDtl_' + @GuidSuffix) + N'
        FROM ErpLab.Erp.InvcDtl AS src
        WHERE src.Company = @pCompany
          AND src.InvoiceNum = @pKey1Int;

        SELECT ' + @ColsCustomer + N'
        INTO dbo.' + QUOTENAME(N'Customer_' + @GuidSuffix) + N'
        FROM (
            SELECT DISTINCT c.*
            FROM ErpLab.Erp.Customer c
            INNER JOIN ErpLab.Erp.InvcHead h
                ON h.Company = c.Company
               AND h.CustNum = c.CustNum
            WHERE h.Company = @pCompany
              AND h.InvoiceNum = @pKey1Int
        ) AS src;

        SELECT ' + @ColsShipTo + N'
        INTO dbo.' + QUOTENAME(N'ShipTo_' + @GuidSuffix) + N'
        FROM (
            SELECT DISTINCT st.*
            FROM ErpLab.Erp.ShipTo st
            INNER JOIN ErpLab.Erp.InvcDtl d
                ON d.Company = st.Company
               AND d.ShipToCustNum = st.CustNum
               AND d.ShipToNum = st.ShipToNum
            WHERE d.Company = @pCompany
              AND d.InvoiceNum = @pKey1Int
        ) AS src;
        ';

        EXEC sp_executesql
            @stmt = @Sql,
            @params = N'@pCompany NVARCHAR(8), @pKey1Int INT',
            @pCompany = @Company,
            @pKey1Int = @Key1Int;

        SET @StagedTablesList = N'RptLabels_' + @GuidSuffix + N',Company_' + @GuidSuffix + N',InvcHead_' + @GuidSuffix + N',InvcDtl_' + @GuidSuffix + N',Customer_' + @GuidSuffix + N',ShipTo_' + @GuidSuffix;
    END

    /* =========================================================================
       BRANCH 4: OpenOrders (BAQ Report Route; @Key1 optional/ignored)
       Staged tables (columns built dynamically from dbo.RddColumn WHERE Exclude = 0):
         - dbo.[RptLabels_<GUID>]
         - dbo.[BAQReportResult_<GUID>] (flattened BAQ output with <Table>_<Field>
           column names [02-baq.md §3.4 / B18] and Calculated_DaysLate computed
           against ErpLab.Erp.LabConstants FixedLabDate using OrderHed.NeedByDate)
       ========================================================================= */
    ELSE IF @ReportType = N'OpenOrders'
    BEGIN
        DECLARE @ColsBAQResult NVARCHAR(MAX);

        SELECT @ColsRptLabels = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'OpenOrders' AND TableName = N'RptLabels' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SELECT @ColsBAQResult = STUFF((
            SELECT N', ' + QUOTENAME(ColumnName)
            FROM dbo.RddColumn
            WHERE RddId = N'OpenOrders' AND TableName = N'BAQReportResult' AND Exclude = 0
            ORDER BY ColumnOrder
            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'), 1, 2, N'');

        SET @Sql = N'
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'RptLabels_'       + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'RptLabels_'       + @GuidSuffix) + N';
        IF OBJECT_ID(''dbo.' + QUOTENAME(N'BAQReportResult_' + @GuidSuffix) + N''', ''U'') IS NOT NULL DROP TABLE dbo.' + QUOTENAME(N'BAQReportResult_' + @GuidSuffix) + N';

        SELECT ' + @ColsRptLabels + N'
        INTO dbo.' + QUOTENAME(N'RptLabels_' + @GuidSuffix) + N'
        FROM (
            SELECT
                CAST(N''ENU''                AS NVARCHAR(10))  AS [RptLanguageID],
                CAST(N''OPEN ORDERS REPORT'' AS NVARCHAR(100)) AS [LblOpenOrdersTitle],
                CAST(N''Customer ID''        AS NVARCHAR(50))  AS [LblCustID],
                CAST(N''Customer Name''      AS NVARCHAR(50))  AS [LblCustName],
                CAST(N''Order #''            AS NVARCHAR(50))  AS [LblOrderNum],
                CAST(N''Order Date''         AS NVARCHAR(50))  AS [LblOrderDate],
                CAST(N''Need By Date''       AS NVARCHAR(50))  AS [LblNeedByDate],
                CAST(N''Days Late''          AS NVARCHAR(50))  AS [LblDaysLate],
                CAST(N''Part Number''        AS NVARCHAR(50))  AS [LblPartNum],
                CAST(N''Description''        AS NVARCHAR(50))  AS [LblLineDesc],
                CAST(N''Open Qty''           AS NVARCHAR(50))  AS [LblOrderQty],
                CAST(N''Unit Price''         AS NVARCHAR(50))  AS [LblUnitPrice]
        ) AS src;

        SELECT ' + @ColsBAQResult + N'
        INTO dbo.' + QUOTENAME(N'BAQReportResult_' + @GuidSuffix) + N'
        FROM (
            SELECT
                c.[CustID]         AS [Customer_CustID],
                c.[Name]           AS [Customer_Name],
                oh.[Company]       AS [OrderHed_Company],
                oh.[OrderNum]      AS [OrderHed_OrderNum],
                oh.[CustNum]       AS [OrderHed_CustNum],
                oh.[PONum]         AS [OrderHed_PONum],
                oh.[OrderDate]     AS [OrderHed_OrderDate],
                oh.[NeedByDate]    AS [OrderHed_NeedByDate],
                oh.[RequestDate]   AS [OrderHed_RequestDate],
                oh.[TermsCode]     AS [OrderHed_TermsCode],
                oh.[ShipToNum]     AS [OrderHed_ShipToNum],
                oh.[OpenOrder]     AS [OrderHed_OpenOrder],
                oh.[OrderAmt]      AS [OrderHed_OrderAmt],
                od.[OrderLine]     AS [OrderDtl_OrderLine],
                od.[PartNum]       AS [OrderDtl_PartNum],
                od.[LineDesc]      AS [OrderDtl_LineDesc],
                od.[OrderQty]      AS [OrderDtl_OrderQty],
                od.[SellingQuantity] AS [OrderDtl_SellingQuantity],
                od.[SalesUM]       AS [OrderDtl_SalesUM],
                od.[UnitPrice]     AS [OrderDtl_UnitPrice],
                od.[DocUnitPrice]  AS [OrderDtl_DocUnitPrice],
                od.[OpenLine]      AS [OrderDtl_OpenLine],
                od.[NeedByDate]    AS [OrderDtl_NeedByDate],
                DATEDIFF(day, oh.[NeedByDate], lc.[ConstantDate]) AS [Calculated_DaysLate]
            FROM ErpLab.Erp.OrderHed oh
            INNER JOIN ErpLab.Erp.OrderDtl od
                ON od.Company = oh.Company
               AND od.OrderNum = oh.OrderNum
            INNER JOIN ErpLab.Erp.Customer c
                ON c.Company = oh.Company
               AND c.CustNum = oh.CustNum
            CROSS JOIN (
                SELECT ConstantDate
                FROM ErpLab.Erp.LabConstants
                WHERE ConstantName = N''FixedLabDate''
            ) lc
            WHERE oh.Company = @pCompany
              AND oh.OpenOrder = 1
              AND oh.VoidOrder = 0
              AND od.OpenLine = 1
              AND od.VoidLine = 0
        ) AS src;
        ';

        EXEC sp_executesql
            @stmt = @Sql,
            @params = N'@pCompany NVARCHAR(8)',
            @pCompany = @Company;

        SET @StagedTablesList = N'RptLabels_' + @GuidSuffix + N',BAQReportResult_' + @GuidSuffix;
    END;

    -- Record staged run in audit tracking table (idempotent if re-staged with same TableGuid)
    IF EXISTS (SELECT 1 FROM dbo.StagedReportRun WHERE TableGuid = @GuidSuffix)
    BEGIN
        UPDATE dbo.StagedReportRun
        SET ReportType   = @ReportType,
            Company      = @Company,
            Key1         = @Key1,
            StagedAtUtc  = SYSUTCDATETIME(),
            StagedTables = @StagedTablesList
        WHERE TableGuid = @GuidSuffix;
    END
    ELSE
    BEGIN
        INSERT INTO dbo.StagedReportRun (TableGuid, ReportType, Company, Key1, StagedTables)
        VALUES (@GuidSuffix, @ReportType, @Company, @Key1, @StagedTablesList);
    END;

    -- Return summary resultset for caller convenience
    SELECT
        @GuidSuffix       AS TableGuid,
        @ReportType       AS ReportType,
        @Company          AS Company,
        @Key1             AS Key1,
        @StagedTablesList AS StagedTables;
END;
GO
