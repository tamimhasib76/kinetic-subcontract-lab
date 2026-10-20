/* =============================================================================
   sql/01-erp-app-schema.sql
   -----------------------------------------------------------------------------
   Application Schema & Mock Business Seed Data
   Target: Microsoft SQL Server 2016+
   Database: [ErpLab]
   Schema:   [Erp]

   Tables (created children-first drop order):
   - Erp.Company
   - Erp.LabConstants
   - Erp.Customer
   - Erp.ShipTo
   - Erp.Part
   - Erp.PartPlant
   - Erp.PartWhse
   - Erp.OrderHed
   - Erp.OrderDtl
   - Erp.OrderRel
   - Erp.ShipHead
   - Erp.ShipDtl
   - Erp.InvcHead
   - Erp.InvcDtl

   Run order:
   1. sql/01-erp-app-schema.sql (creates ErpLab database, schema, tables, seed data)
   2. sql/02-erp-rpt-staging.sql (creates ErpReporting database and staging procedure)
   ============================================================================= */

SET NOCOUNT ON;

-- Ensure database [ErpLab] exists
IF DB_ID('ErpLab') IS NULL
BEGIN
    CREATE DATABASE [ErpLab];
END;
GO

USE [ErpLab];
GO

-- Ensure schema [Erp] exists
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'Erp')
BEGIN
    EXEC('CREATE SCHEMA [Erp]');
END;
GO

/* =============================================================================
   1. TABLE CLEANUP (Children-First Drop)
   ============================================================================= */

IF OBJECT_ID('Erp.InvcDtl', 'U') IS NOT NULL DROP TABLE Erp.InvcDtl;
IF OBJECT_ID('Erp.InvcHead', 'U') IS NOT NULL DROP TABLE Erp.InvcHead;
IF OBJECT_ID('Erp.ShipDtl', 'U') IS NOT NULL DROP TABLE Erp.ShipDtl;
IF OBJECT_ID('Erp.ShipHead', 'U') IS NOT NULL DROP TABLE Erp.ShipHead;
IF OBJECT_ID('Erp.OrderRel', 'U') IS NOT NULL DROP TABLE Erp.OrderRel;
IF OBJECT_ID('Erp.OrderDtl', 'U') IS NOT NULL DROP TABLE Erp.OrderDtl;
IF OBJECT_ID('Erp.OrderHed', 'U') IS NOT NULL DROP TABLE Erp.OrderHed;
IF OBJECT_ID('Erp.PartWhse', 'U') IS NOT NULL DROP TABLE Erp.PartWhse;
IF OBJECT_ID('Erp.PartPlant', 'U') IS NOT NULL DROP TABLE Erp.PartPlant;
IF OBJECT_ID('Erp.Part', 'U') IS NOT NULL DROP TABLE Erp.Part;
IF OBJECT_ID('Erp.ShipTo', 'U') IS NOT NULL DROP TABLE Erp.ShipTo;
IF OBJECT_ID('Erp.Customer', 'U') IS NOT NULL DROP TABLE Erp.Customer;
IF OBJECT_ID('Erp.LabConstants', 'U') IS NOT NULL DROP TABLE Erp.LabConstants;
IF OBJECT_ID('Erp.Company', 'U') IS NOT NULL DROP TABLE Erp.Company;
GO

/* =============================================================================
   2. TABLE DEFINITIONS
   ============================================================================= */

-- 2.1 Erp.Company
CREATE TABLE Erp.Company (
    Company             NVARCHAR(8)   NOT NULL,
    Name                NVARCHAR(50)  NOT NULL,
    Address1            NVARCHAR(50)  NULL,
    Address2            NVARCHAR(50)  NULL,
    City                NVARCHAR(50)  NULL,
    State               NVARCHAR(50)  NULL,
    Zip                 NVARCHAR(20)  NULL,
    Country             NVARCHAR(50)  NULL,
    PhoneNum            NVARCHAR(30)  NULL,
    FiscalCalendarID    NVARCHAR(10)  NULL,
    CONSTRAINT PK_Erp_Company PRIMARY KEY CLUSTERED (Company)
);

-- 2.2 Erp.LabConstants
CREATE TABLE Erp.LabConstants (
    ConstantName        NVARCHAR(50)  NOT NULL,
    ConstantValue       NVARCHAR(100) NOT NULL,
    ConstantDate        DATE          NULL,
    Description         NVARCHAR(250) NULL,
    CONSTRAINT PK_Erp_LabConstants PRIMARY KEY CLUSTERED (ConstantName)
);

-- 2.3 Erp.Customer
CREATE TABLE Erp.Customer (
    Company             NVARCHAR(8)   NOT NULL,
    CustNum             INT           NOT NULL,
    CustID              NVARCHAR(20)  NOT NULL,
    Name                NVARCHAR(50)  NOT NULL,
    Address1            NVARCHAR(50)  NULL,
    Address2            NVARCHAR(50)  NULL,
    City                NVARCHAR(50)  NULL,
    State               NVARCHAR(50)  NULL,
    Zip                 NVARCHAR(20)  NULL,
    Country             NVARCHAR(50)  NULL,
    PhoneNum            NVARCHAR(30)  NULL,
    TermsCode           NVARCHAR(10)  NULL,
    TerritoryID         NVARCHAR(10)  NULL,
    CustType            NVARCHAR(10)  NULL,
    AccountManager_c    NVARCHAR(50)  NULL,
    CONSTRAINT PK_Erp_Customer PRIMARY KEY CLUSTERED (Company, CustNum),
    CONSTRAINT UQ_Erp_Customer_CustID UNIQUE (Company, CustID),
    CONSTRAINT FK_Erp_Customer_Company FOREIGN KEY (Company) REFERENCES Erp.Company (Company)
);

-- 2.4 Erp.ShipTo
CREATE TABLE Erp.ShipTo (
    Company             NVARCHAR(8)   NOT NULL,
    CustNum             INT           NOT NULL,
    ShipToNum           NVARCHAR(14)  NOT NULL,
    Name                NVARCHAR(50)  NOT NULL,
    Address1            NVARCHAR(50)  NULL,
    Address2            NVARCHAR(50)  NULL,
    City                NVARCHAR(50)  NULL,
    State               NVARCHAR(50)  NULL,
    Zip                 NVARCHAR(20)  NULL,
    Country             NVARCHAR(50)  NULL,
    TerritoryID         NVARCHAR(10)  NULL,
    SpecialInstructions_c NVARCHAR(250) NULL,
    CONSTRAINT PK_Erp_ShipTo PRIMARY KEY CLUSTERED (Company, CustNum, ShipToNum),
    CONSTRAINT FK_Erp_ShipTo_Customer FOREIGN KEY (Company, CustNum) REFERENCES Erp.Customer (Company, CustNum)
);

-- 2.5 Erp.Part
CREATE TABLE Erp.Part (
    Company             NVARCHAR(8)    NOT NULL,
    PartNum             NVARCHAR(50)   NOT NULL,
    PartDescription     NVARCHAR(1000) NOT NULL,
    ClassID             NVARCHAR(10)   NULL,
    TypeCode            NVARCHAR(1)    NULL,
    IUM                 NVARCHAR(6)    NOT NULL,
    PUM                 NVARCHAR(6)    NOT NULL,
    SalesUM             NVARCHAR(6)    NOT NULL,
    PricePerCode        NVARCHAR(1)    NULL,
    UnitPrice           DECIMAL(15, 5) NOT NULL DEFAULT 0.00000,
    TrackLots           BIT            NOT NULL DEFAULT 0,
    TrackSerialNum      BIT            NOT NULL DEFAULT 0,
    SteelGauge_c        NVARCHAR(20)   NULL,
    PPAP_c              BIT            NOT NULL DEFAULT 0,
    CONSTRAINT PK_Erp_Part PRIMARY KEY CLUSTERED (Company, PartNum),
    CONSTRAINT FK_Erp_Part_Company FOREIGN KEY (Company) REFERENCES Erp.Company (Company)
);

-- 2.6 Erp.PartPlant
CREATE TABLE Erp.PartPlant (
    Company             NVARCHAR(8)   NOT NULL,
    PartNum             NVARCHAR(50)  NOT NULL,
    Plant               NVARCHAR(8)   NOT NULL,
    PrimWhse            NVARCHAR(8)   NOT NULL,
    CostMethod          NVARCHAR(1)   NULL,
    LeadTime            INT           NOT NULL DEFAULT 0,
    MfgLeadDays_c       INT           NULL,
    CONSTRAINT PK_Erp_PartPlant PRIMARY KEY CLUSTERED (Company, PartNum, Plant),
    CONSTRAINT FK_Erp_PartPlant_Part FOREIGN KEY (Company, PartNum) REFERENCES Erp.Part (Company, PartNum)
);

-- 2.7 Erp.PartWhse
CREATE TABLE Erp.PartWhse (
    Company             NVARCHAR(8)    NOT NULL,
    PartNum             NVARCHAR(50)   NOT NULL,
    Plant               NVARCHAR(8)    NOT NULL,
    WarehouseCode       NVARCHAR(8)    NOT NULL,
    PrimBin             NVARCHAR(10)   NULL,
    OnHandQty           DECIMAL(15, 4) NOT NULL DEFAULT 0.0000,
    CycleCountCategory_c NVARCHAR(10)  NULL,
    CONSTRAINT PK_Erp_PartWhse PRIMARY KEY CLUSTERED (Company, PartNum, Plant, WarehouseCode),
    CONSTRAINT FK_Erp_PartWhse_PartPlant FOREIGN KEY (Company, PartNum, Plant) REFERENCES Erp.PartPlant (Company, PartNum, Plant)
);

-- 2.8 Erp.OrderHed
CREATE TABLE Erp.OrderHed (
    Company             NVARCHAR(8)    NOT NULL,
    OrderNum            INT            NOT NULL,
    CustNum             INT            NOT NULL,
    PONum               NVARCHAR(50)   NULL,
    OrderDate           DATE           NOT NULL,
    NeedByDate          DATE           NOT NULL,
    RequestDate         DATE           NOT NULL,
    TermsCode           NVARCHAR(10)   NULL,
    ShipToNum           NVARCHAR(14)   NULL,
    OpenOrder           BIT            NOT NULL DEFAULT 1,
    VoidOrder           BIT            NOT NULL DEFAULT 0,
    OrderAmt            DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    RptLanguageID       NVARCHAR(10)   NOT NULL DEFAULT 'ENU',
    ProjManager_c       NVARCHAR(50)   NULL,
    CONSTRAINT PK_Erp_OrderHed PRIMARY KEY CLUSTERED (Company, OrderNum),
    CONSTRAINT FK_Erp_OrderHed_Customer FOREIGN KEY (Company, CustNum) REFERENCES Erp.Customer (Company, CustNum)
);

-- 2.9 Erp.OrderDtl
CREATE TABLE Erp.OrderDtl (
    Company             NVARCHAR(8)    NOT NULL,
    OrderNum            INT            NOT NULL,
    OrderLine           INT            NOT NULL,
    PartNum             NVARCHAR(50)   NOT NULL,
    LineDesc            NVARCHAR(1000) NULL,
    OrderQty            DECIMAL(15, 4) NOT NULL DEFAULT 1.0000,
    SellingQuantity     DECIMAL(15, 4) NOT NULL DEFAULT 1.0000,
    SalesUM             NVARCHAR(6)    NOT NULL DEFAULT 'EA',
    UnitPrice           DECIMAL(15, 5) NOT NULL DEFAULT 0.00000,
    DocUnitPrice        DECIMAL(15, 5) NOT NULL DEFAULT 0.00000,
    DspUnitPrice        DECIMAL(15, 5) NOT NULL DEFAULT 0.00000,
    OpenLine            BIT            NOT NULL DEFAULT 1,
    VoidLine            BIT            NOT NULL DEFAULT 0,
    NeedByDate          DATE           NULL,
    RequestDate         DATE           NULL,
    RevisionNum         NVARCHAR(10)   NOT NULL DEFAULT 'A',
    ExtWeight           DECIMAL(15, 4) NOT NULL DEFAULT 0.0000,
    FabricationNotes_c  NVARCHAR(500)  NULL,
    CONSTRAINT PK_Erp_OrderDtl PRIMARY KEY CLUSTERED (Company, OrderNum, OrderLine),
    CONSTRAINT FK_Erp_OrderDtl_OrderHed FOREIGN KEY (Company, OrderNum) REFERENCES Erp.OrderHed (Company, OrderNum),
    CONSTRAINT FK_Erp_OrderDtl_Part FOREIGN KEY (Company, PartNum) REFERENCES Erp.Part (Company, PartNum)
);

-- 2.10 Erp.OrderRel
CREATE TABLE Erp.OrderRel (
    Company             NVARCHAR(8)    NOT NULL,
    OrderNum            INT            NOT NULL,
    OrderLine           INT            NOT NULL,
    OrderRelNum         INT            NOT NULL,
    OurReqQty           DECIMAL(15, 4) NOT NULL DEFAULT 1.0000,
    SellingReqQty       DECIMAL(15, 4) NOT NULL DEFAULT 1.0000,
    ShipToNum           NVARCHAR(14)   NULL,
    ShipToCustNum       INT            NULL,
    NeedByDate          DATE           NULL,
    ReqDate             DATE           NULL,
    OpenRelease         BIT            NOT NULL DEFAULT 1,
    FirmRelease         BIT            NOT NULL DEFAULT 1,
    Plant               NVARCHAR(8)    NULL,
    WarehouseCode       NVARCHAR(8)    NULL,
    RelHoldReason_c     NVARCHAR(50)   NULL,
    CONSTRAINT PK_Erp_OrderRel PRIMARY KEY CLUSTERED (Company, OrderNum, OrderLine, OrderRelNum),
    CONSTRAINT FK_Erp_OrderRel_OrderDtl FOREIGN KEY (Company, OrderNum, OrderLine) REFERENCES Erp.OrderDtl (Company, OrderNum, OrderLine)
);

-- 2.11 Erp.ShipHead
CREATE TABLE Erp.ShipHead (
    Company             NVARCHAR(8)    NOT NULL,
    PackNum             INT            NOT NULL,
    CustNum             INT            NOT NULL,
    ShipDate            DATE           NOT NULL,
    ShipToNum           NVARCHAR(14)   NULL,
    ShipToCustNum       INT            NULL,
    ShipStatus          NVARCHAR(10)   NOT NULL DEFAULT 'SHIPPED',
    TrackingNumber      NVARCHAR(50)   NULL,
    ShipViaCode         NVARCHAR(10)   NULL,
    Weight              DECIMAL(15, 4) NOT NULL DEFAULT 0.0000,
    RptLanguageID       NVARCHAR(10)   NOT NULL DEFAULT 'ENU',
    CarrierTrackingUrl_c NVARCHAR(250) NULL,
    CONSTRAINT PK_Erp_ShipHead PRIMARY KEY CLUSTERED (Company, PackNum),
    CONSTRAINT FK_Erp_ShipHead_Customer FOREIGN KEY (Company, CustNum) REFERENCES Erp.Customer (Company, CustNum)
);

-- 2.12 Erp.ShipDtl
CREATE TABLE Erp.ShipDtl (
    Company             NVARCHAR(8)    NOT NULL,
    PackNum             INT            NOT NULL,
    PackLine            INT            NOT NULL,
    OrderNum            INT            NOT NULL,
    OrderLine           INT            NOT NULL,
    OrderRelNum         INT            NOT NULL,
    PartNum             NVARCHAR(50)   NOT NULL,
    LineDesc            NVARCHAR(1000) NULL,
    OurInventoryShipQty DECIMAL(15, 4) NOT NULL DEFAULT 1.0000,
    SellingShippedQty   DECIMAL(15, 4) NOT NULL DEFAULT 1.0000,
    Packages            INT            NOT NULL DEFAULT 1,
    IUM                 NVARCHAR(6)    NOT NULL DEFAULT 'EA',
    SalesUM             NVARCHAR(6)    NOT NULL DEFAULT 'EA',
    CustPartNum         NVARCHAR(50)   NULL,
    HeatNumber_c        NVARCHAR(50)   NULL,
    CertificateOfConformance_c BIT     NOT NULL DEFAULT 0,
    CONSTRAINT PK_Erp_ShipDtl PRIMARY KEY CLUSTERED (Company, PackNum, PackLine),
    CONSTRAINT FK_Erp_ShipDtl_ShipHead FOREIGN KEY (Company, PackNum) REFERENCES Erp.ShipHead (Company, PackNum)
);

-- 2.13 Erp.InvcHead
CREATE TABLE Erp.InvcHead (
    Company             NVARCHAR(8)    NOT NULL,
    InvoiceNum          INT            NOT NULL,
    CustNum             INT            NOT NULL,
    InvoiceDate         DATE           NOT NULL,
    OrderNum            INT            NULL,
    InvoiceType         NVARCHAR(10)   NOT NULL DEFAULT 'STD',
    InvoiceAmt          DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    TermsCode           NVARCHAR(10)   NULL,
    OpenInvoice         BIT            NOT NULL DEFAULT 1,
    RptLanguageID       NVARCHAR(10)   NOT NULL DEFAULT 'ENU',
    RemitToName         NVARCHAR(100)  NOT NULL DEFAULT 'ErpLab Remittance Processing',
    RemitToAddress1     NVARCHAR(100)  NOT NULL DEFAULT 'P.O. Box 75000',
    RemitToCity         NVARCHAR(50)   NOT NULL DEFAULT 'Chicago',
    RemitToState        NVARCHAR(10)   NOT NULL DEFAULT 'IL',
    RemitToZip          NVARCHAR(20)   NOT NULL DEFAULT '60675',
    ShipToPONum_c       NVARCHAR(50)   NULL,
    BillingContact_c    NVARCHAR(50)   NULL,
    CONSTRAINT PK_Erp_InvcHead PRIMARY KEY CLUSTERED (Company, InvoiceNum),
    CONSTRAINT FK_Erp_InvcHead_Customer FOREIGN KEY (Company, CustNum) REFERENCES Erp.Customer (Company, CustNum)
);

-- 2.14 Erp.InvcDtl
CREATE TABLE Erp.InvcDtl (
    Company             NVARCHAR(8)    NOT NULL,
    InvoiceNum          INT            NOT NULL,
    InvoiceLine         INT            NOT NULL,
    OrderNum            INT            NULL,
    OrderLine           INT            NULL,
    OrderRelNum         INT            NULL,
    PackNum             INT            NULL,
    PackLine            INT            NULL,
    PartNum             NVARCHAR(50)   NOT NULL,
    LineDesc            NVARCHAR(1000) NULL,
    SellingShipQty      DECIMAL(15, 4) NOT NULL DEFAULT 1.0000,
    UnitPrice           DECIMAL(15, 5) NOT NULL DEFAULT 0.00000,
    DocUnitPrice        DECIMAL(15, 5) NOT NULL DEFAULT 0.00000,
    ExtPrice            DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    ShipToCustNum       INT            NULL,
    ShipToNum           NVARCHAR(14)   NULL,
    GLAnalysisCode_c    NVARCHAR(20)   NULL,
    CONSTRAINT PK_Erp_InvcDtl PRIMARY KEY CLUSTERED (Company, InvoiceNum, InvoiceLine),
    CONSTRAINT FK_Erp_InvcDtl_InvcHead FOREIGN KEY (Company, InvoiceNum) REFERENCES Erp.InvcHead (Company, InvoiceNum)
);
GO

/* =============================================================================
   3. SEED DATA GENERATION
   ============================================================================= */

-- 3.0 Reference Constants
INSERT INTO Erp.LabConstants (ConstantName, ConstantValue, ConstantDate, Description)
VALUES ('FixedLabDate', '20261015', '20261015', 'Fixed lab reference date for order aging and status calculations');

-- 3.1 Operating Companies
INSERT INTO Erp.Company (Company, Name, Address1, City, State, Zip, Country, PhoneNum, FiscalCalendarID)
VALUES 
('MFG01', 'MFG01 Manufacturing Corp',       '100 Industrial Pkwy', 'Cleveland',    'OH', '44101', 'USA', '216-555-0101', 'MAIN'),
('MFG02', 'MFG02 Precision Technologies LLC', '200 Precision Way',   'Grand Rapids', 'MI', '49501', 'USA', '616-555-0202', 'MAIN');

-- 3.2 Customers
-- MFG01 Customer Accounts
INSERT INTO Erp.Customer (Company, CustNum, CustID, Name, Address1, City, State, Zip, Country, TermsCode, AccountManager_c)
VALUES
('MFG01', 1,  'CUST01',    'Acme Industrial Technologies', '500 Tech Blvd', 'Cleveland', 'OH', '44114', 'USA', 'N30', 'Sarah Connor'),
('MFG01', 2,  'CUST02',    'Global Precision Aerospace',   '1200 Aero Way', 'Akron', 'OH', '44301', 'USA', 'N60', 'Ellen Ripley'),
('MFG01', 3,  'CUST03',    'Pinnacle Machinery Corp',      '3400 Factory Rd', 'Toledo', 'OH', '43601', 'USA', 'N30', 'Rick Deckard'),
('MFG01', 4,  'CUST04',    'Vortex Heavy Engineering',     '800 Turbine St', 'Canton', 'OH', '44701', 'USA', 'N45', 'Dana Scully'),
('MFG01', 5,  'CUST05',    'Apex Dynamics Ltd',            '900 Summit Ave', 'Youngstown', 'OH', '44501', 'USA', 'N30', 'James Holden'),
('MFG01', 6,  'M1-CUST06', 'Buckeye State Stamping',       '111 Erie St', 'Cleveland', 'OH', '44113', 'USA', 'N30', 'Sarah Connor'),
('MFG01', 7,  'M1-CUST07', 'Erie Die & Tooling',           '222 High St', 'Columbus', 'OH', '43215', 'USA', 'N30', 'Ellen Ripley'),
('MFG01', 8,  'M1-CUST08', 'Cleveland Laser Works',        '333 Lake Ave', 'Cleveland', 'OH', '44102', 'USA', 'N30', 'Rick Deckard'),
('MFG01', 9,  'M1-CUST09', 'Akron Polymer Molding',        '444 Rubber Rd', 'Akron', 'OH', '44308', 'USA', 'N30', 'Dana Scully'),
('MFG01', 10, 'M1-CUST10', 'Canton Foundry & Forge',       '555 Cast Way', 'Canton', 'OH', '44702', 'USA', 'N30', 'James Holden'),
('MFG01', 11, 'M1-CUST11', 'Dayton Industrial Controls',   '666 Aviation Blvd', 'Dayton', 'OH', '45402', 'USA', 'N30', 'Sarah Connor'),
('MFG01', 12, 'M1-CUST12', 'Toledo Gear Systems',          '777 Transmission St', 'Toledo', 'OH', '43604', 'USA', 'N30', 'Ellen Ripley'),
('MFG01', 13, 'M1-CUST13', 'Youngstown Steel Fabricators', '888 Furnace Dr', 'Youngstown', 'OH', '44503', 'USA', 'N30', 'Rick Deckard'),
('MFG01', 14, 'M1-CUST14', 'Mansfield Sheet Metal',        '999 Press Ave', 'Mansfield', 'OH', '44902', 'USA', 'N30', 'Dana Scully'),
('MFG01', 15, 'M1-CUST15', 'Lorain Marine Hardware',       '101 Harbor View', 'Lorain', 'OH', '44052', 'USA', 'N30', 'James Holden'),
('MFG01', 16, 'M1-CUST16', 'Sandusky Valve & Fitting',     '202 Bay Point', 'Sandusky', 'OH', '44870', 'USA', 'N30', 'Sarah Connor'),
('MFG01', 17, 'M1-CUST17', 'Warren Assembly Automation',   '303 Line Rd', 'Warren', 'OH', '44483', 'USA', 'N30', 'Ellen Ripley'),
('MFG01', 18, 'M1-CUST18', 'Lima Engine Components',       '404 Piston Dr', 'Lima', 'OH', '45801', 'USA', 'N30', 'Rick Deckard'),
('MFG01', 19, 'M1-CUST19', 'Marion Material Handling',     '505 Conveyor Way', 'Marion', 'OH', '43302', 'USA', 'N30', 'Dana Scully'),
('MFG01', 20, 'M1-CUST20', 'Hamilton Hydraulic Power',     '606 Fluid St', 'Hamilton', 'OH', '45011', 'USA', 'N30', 'James Holden'),
-- Additional regional commercial accounts
('MFG01', 21, '10',        'Precision Dynamics 10',        '701 Commerce Ct', 'Columbus', 'OH', '43201', 'USA', 'N30', 'Sarah Connor'),
('MFG01', 22, '12',        'Precision Dynamics 12',        '702 Commerce Ct', 'Columbus', 'OH', '43201', 'USA', 'N30', 'Ellen Ripley'),
('MFG01', 23, '15',        'Precision Dynamics 15',        '703 Commerce Ct', 'Columbus', 'OH', '43201', 'USA', 'N30', 'Rick Deckard');

-- MFG02 Customer Accounts
INSERT INTO Erp.Customer (Company, CustNum, CustID, Name, Address1, City, State, Zip, Country, TermsCode, AccountManager_c)
VALUES
('MFG02', 1,  'M2-CUST01', 'Michigan Rotor Works',         '101 Rotor Way', 'Detroit', 'MI', '48202', 'USA', 'N30', 'John Connor'),
('MFG02', 2,  'M2-CUST02', 'Grand Rapids Tool & Die',      '202 Precision Ave', 'Grand Rapids', 'MI', '49503', 'USA', 'N60', 'Arthur Dallas'),
('MFG02', 3,  'M2-CUST03', 'Detroit Gear & Axle',          '303 Powertrain Blvd', 'Detroit', 'MI', '48211', 'USA', 'N30', 'Rachael Tyrell'),
('MFG02', 4,  'M2-CUST04', 'Lansing Assembly Systems',     '404 Robotic Dr', 'Lansing', 'MI', '48912', 'USA', 'N45', 'Fox Mulder'),
('MFG02', 5,  'M2-CUST05', 'Huron Industrial Hydraulics',  '505 Valve Rd', 'Port Huron', 'MI', '48060', 'USA', 'N30', 'Naomi Nagata'),
('MFG02', 6,  'CUST01',    'Acme Global Midwest Division', '502 Tech Blvd', 'Detroit', 'MI', '48201', 'USA', 'N30', 'John Connor'),
('MFG02', 7,  'CUST02',    'Global Precision Propulsion',  '1210 Aero Way', 'Grand Rapids', 'MI', '49512', 'USA', 'N60', 'Arthur Dallas'),
('MFG02', 8,  'CUST03',    'Pinnacle Automation Robotics', '3410 Automation Dr', 'Lansing', 'MI', '48901', 'USA', 'N30', 'Rachael Tyrell'),
('MFG02', 9,  'CUST04',    'Vortex Marine Engineering',    '820 Harbor Rd', 'Holland', 'MI', '49423', 'USA', 'N45', 'Fox Mulder'),
('MFG02', 10, 'CUST05',    'Apex Dynamics Aerospace',      '910 Summit Ave', 'Kalamazoo', 'MI', '49001', 'USA', 'N30', 'Naomi Nagata'),
('MFG02', 11, 'M2-CUST11', 'Kalamazoo Automation Corp',    '111 Instrument St', 'Kalamazoo', 'MI', '49007', 'USA', 'N30', 'John Connor'),
('MFG02', 12, 'M2-CUST12', 'Flint Powertrain Dynamics',    '222 Assembly Rd', 'Flint', 'MI', '48503', 'USA', 'N30', 'Arthur Dallas'),
('MFG02', 13, 'M2-CUST13', 'Saginaw Steering Solutions',   '333 Rack Ave', 'Saginaw', 'MI', '48601', 'USA', 'N30', 'Rachael Tyrell'),
('MFG02', 14, 'M2-CUST14', 'Muskegon Piston Ring',         '444 Casting Blvd', 'Muskegon', 'MI', '49441', 'USA', 'N30', 'Fox Mulder'),
('MFG02', 15, 'M2-CUST15', 'Battle Creek Machinery',       '555 Processing Way', 'Battle Creek', 'MI', '49014', 'USA', 'N30', 'Naomi Nagata'),
('MFG02', 16, 'M2-CUST16', 'Ann Arbor Robotics Lab',       '666 Tech Park Dr', 'Ann Arbor', 'MI', '48105', 'USA', 'N30', 'John Connor'),
('MFG02', 17, 'M2-CUST17', 'Dearborn Stamping Press',      '777 Rouge St', 'Dearborn', 'MI', '48120', 'USA', 'N30', 'Arthur Dallas'),
('MFG02', 18, 'M2-CUST18', 'Troy Engineering Group',       '888 Big Beaver Rd', 'Troy', 'MI', '48084', 'USA', 'N30', 'Rachael Tyrell'),
('MFG02', 19, 'M2-CUST19', 'Pontiac Motor Spares',         '999 Wide Track Dr', 'Pontiac', 'MI', '48342', 'USA', 'N30', 'Fox Mulder'),
('MFG02', 20, 'M2-CUST20', 'Bay City Rigging & Crane',     '101 Shipyard Way', 'Bay City', 'MI', '48706', 'USA', 'N30', 'Naomi Nagata'),
-- Additional regional commercial accounts
('MFG02', 21, '11',        'Precision Dynamics 11',        '801 Commerce Ln', 'Detroit', 'MI', '48226', 'USA', 'N30', 'John Connor'),
('MFG02', 22, '14',        'Precision Dynamics 14',        '802 Commerce Ln', 'Detroit', 'MI', '48226', 'USA', 'N30', 'Arthur Dallas'),
('MFG02', 23, '17',        'Precision Dynamics 17',        '803 Commerce Ln', 'Detroit', 'MI', '48226', 'USA', 'N30', 'Rachael Tyrell');

-- 3.3 ShipTo Addresses
INSERT INTO Erp.ShipTo (Company, CustNum, ShipToNum, Name, Address1, City, State, Zip, Country, SpecialInstructions_c)
SELECT Company, CustNum, 'MAIN', Name + ' Dock 1', Address1, City, State, Zip, Country, 'Deliver to receiving dock 1'
FROM Erp.Customer;

INSERT INTO Erp.ShipTo (Company, CustNum, ShipToNum, Name, Address1, City, State, Zip, Country, SpecialInstructions_c)
SELECT Company, CustNum, 'PLANT2', Name + ' Facility B', 'Bldg 2 ' + Address1, City, State, Zip, Country, 'Requires lift gate'
FROM Erp.Customer
WHERE CustNum IN (1, 2, 6, 7);

-- 3.4 Parts
INSERT INTO Erp.Part (Company, PartNum, PartDescription, ClassID, TypeCode, IUM, PUM, SalesUM, UnitPrice, SteelGauge_c, PPAP_c)
VALUES
('MFG01', 'PART-100', 'Standard Structural Bracket 100mm', 'STAMP', 'M', 'EA', 'EA', 'EA', 12.50000, '12 GA', 1),
('MFG02', 'PART-100', 'Standard Structural Bracket 100mm', 'STAMP', 'M', 'EA', 'EA', 'EA', 13.00000, '12 GA', 1),

('MFG01', 'PART-200', 'Heavy Duty Flange Assembly 200mm', 'MACH', 'M', 'EA', 'EA', 'EA', 45.75000, '1/4 IN', 1),
('MFG02', 'PART-200', 'Heavy Duty Flange Assembly 200mm', 'MACH', 'M', 'EA', 'EA', 'EA', 44.50000, '1/4 IN', 1),

('MFG01', 'PART-300', 'Precision Bearing Carrier Base', 'MACH', 'M', 'EA', 'EA', 'EA', 85.00000, '10 GA', 0),
('MFG02', 'PART-300', 'Precision Bearing Carrier Base', 'MACH', 'M', 'EA', 'EA', 'EA', 88.00000, '10 GA', 0),

('MFG01', 'SUB-01', 'Subcontract Chrome Plated Housing', 'SUBC', 'M', 'EA', 'EA', 'EA', 120.00000, '16 GA', 1),
('MFG02', 'SUB-01', 'Subcontract Chrome Plated Housing', 'SUBC', 'M', 'EA', 'EA', 'EA', 125.00000, '16 GA', 1),

('MFG01', 'WIDGET-01', 'Sensor Mounting Clip SS304', 'FAB', 'M', 'EA', 'EA', 'EA', 6.25000, '18 GA', 0),
('MFG02', 'WIDGET-01', 'Sensor Mounting Clip SS304', 'FAB', 'M', 'EA', 'EA', 'EA', 6.50000, '18 GA', 0),

('MFG01', 'MFG1-SPECIAL-01', 'Special Ohio Stamped Arm', 'STAMP', 'M', 'EA', 'EA', 'EA', 22.00000, '14 GA', 0),
('MFG01', 'MFG1-SPECIAL-02', 'Special Ohio Laser Cut Plate', 'PLATE', 'M', 'EA', 'EA', 'EA', 35.00000, '3/8 IN', 1),
('MFG02', 'MFG2-CUSTOM-01',  'Custom Michigan Weldment',   'WELD',  'M', 'EA', 'EA', 'EA', 150.00000, '11 GA', 1),
('MFG02', 'MFG2-CUSTOM-02',  'Custom Michigan Drive Axle',  'MACH',  'M', 'EA', 'EA', 'EA', 210.00000, 'SOLID', 1);

-- 3.5 PartPlant & PartWhse
INSERT INTO Erp.PartPlant (Company, PartNum, Plant, PrimWhse, CostMethod, LeadTime, MfgLeadDays_c)
SELECT Company, PartNum, CASE WHEN Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END, 'MAIN', 'S', 10, 5
FROM Erp.Part;

INSERT INTO Erp.PartWhse (Company, PartNum, Plant, WarehouseCode, PrimBin, OnHandQty, CycleCountCategory_c)
SELECT Company, PartNum, Plant, 'MAIN', 'A-01-01', 500.0000, 'A'
FROM Erp.PartPlant;

INSERT INTO Erp.PartWhse (Company, PartNum, Plant, WarehouseCode, PrimBin, OnHandQty, CycleCountCategory_c)
SELECT Company, PartNum, Plant, 'SHP', 'DOCK-1', 100.0000, 'B'
FROM Erp.PartPlant;

-- 3.6 Sales Orders (150 orders per operating company)
;WITH Tally150 AS (
    SELECT TOP (150) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS Num
    FROM (VALUES(1),(1),(1),(1),(1),(1),(1),(1),(1),(1)) a(n)
    CROSS JOIN (VALUES(1),(1),(1),(1),(1),(1),(1),(1),(1),(1)) b(n)
    CROSS JOIN (VALUES(1),(1),(1),(1)) c(n)
)
-- MFG01 Orders (10001 to 10150)
INSERT INTO Erp.OrderHed (Company, OrderNum, CustNum, PONum, OrderDate, NeedByDate, RequestDate, TermsCode, ShipToNum, OpenOrder, VoidOrder, OrderAmt, RptLanguageID, ProjManager_c)
SELECT 
    'MFG01',
    10000 + t.Num,
    ((t.Num - 1) % 23) + 1,
    'PO-M1-' + RIGHT('0000' + CAST(t.Num AS VARCHAR(10)), 4),
    CASE 
        WHEN t.Num <= 60 THEN DATEADD(day, - (120 - t.Num), '20260901')
        WHEN t.Num <= 100 THEN DATEADD(day, - (105 - t.Num), '20260920')
        ELSE DATEADD(day, - (155 - t.Num), '20261001')
    END,
    CASE 
        WHEN t.Num <= 60 THEN DATEADD(day, - (100 - t.Num), '20260915')
        WHEN t.Num BETWEEN 61 AND 75 THEN DATEADD(day, - (76 - t.Num), '20261014')
        WHEN t.Num BETWEEN 76 AND 100 THEN DATEADD(day, (t.Num - 75) * 2, '20261016')
        WHEN t.Num BETWEEN 101 AND 115 THEN DATEADD(day, - (116 - t.Num), '20261014')
        ELSE DATEADD(day, (t.Num - 115) * 2, '20261016')
    END,
    CASE 
        WHEN t.Num <= 60 THEN DATEADD(day, - (100 - t.Num), '20260915')
        WHEN t.Num BETWEEN 61 AND 75 THEN DATEADD(day, - (76 - t.Num), '20261014')
        WHEN t.Num BETWEEN 76 AND 100 THEN DATEADD(day, (t.Num - 75) * 2, '20261016')
        WHEN t.Num BETWEEN 101 AND 115 THEN DATEADD(day, - (116 - t.Num), '20261014')
        ELSE DATEADD(day, (t.Num - 115) * 2, '20261016')
    END,
    'N30',
    'MAIN',
    CASE WHEN t.Num <= 60 THEN 0 ELSE 1 END,
    0,
    0.00,
    'ENU',
    'Sarah Connor'
FROM Tally150 t;

;WITH Tally150 AS (
    SELECT TOP (150) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS Num
    FROM (VALUES(1),(1),(1),(1),(1),(1),(1),(1),(1),(1)) a(n)
    CROSS JOIN (VALUES(1),(1),(1),(1),(1),(1),(1),(1),(1),(1)) b(n)
    CROSS JOIN (VALUES(1),(1),(1),(1)) c(n)
)
-- MFG02 Orders (20001 to 20150)
INSERT INTO Erp.OrderHed (Company, OrderNum, CustNum, PONum, OrderDate, NeedByDate, RequestDate, TermsCode, ShipToNum, OpenOrder, VoidOrder, OrderAmt, RptLanguageID, ProjManager_c)
SELECT 
    'MFG02',
    20000 + t.Num,
    ((t.Num - 1) % 23) + 1,
    'PO-M2-' + RIGHT('0000' + CAST(t.Num AS VARCHAR(10)), 4),
    CASE 
        WHEN t.Num <= 60 THEN DATEADD(day, - (120 - t.Num), '20260901')
        WHEN t.Num <= 100 THEN DATEADD(day, - (105 - t.Num), '20260920')
        ELSE DATEADD(day, - (155 - t.Num), '20261001')
    END,
    CASE 
        WHEN t.Num <= 60 THEN DATEADD(day, - (100 - t.Num), '20260915')
        WHEN t.Num BETWEEN 61 AND 75 THEN DATEADD(day, - (76 - t.Num), '20261014')
        WHEN t.Num BETWEEN 76 AND 100 THEN DATEADD(day, (t.Num - 75) * 2, '20261016')
        WHEN t.Num BETWEEN 101 AND 115 THEN DATEADD(day, - (116 - t.Num), '20261014')
        ELSE DATEADD(day, (t.Num - 115) * 2, '20261016')
    END,
    CASE 
        WHEN t.Num <= 60 THEN DATEADD(day, - (100 - t.Num), '20260915')
        WHEN t.Num BETWEEN 61 AND 75 THEN DATEADD(day, - (76 - t.Num), '20261014')
        WHEN t.Num BETWEEN 76 AND 100 THEN DATEADD(day, (t.Num - 75) * 2, '20261016')
        WHEN t.Num BETWEEN 101 AND 115 THEN DATEADD(day, - (116 - t.Num), '20261014')
        ELSE DATEADD(day, (t.Num - 115) * 2, '20261016')
    END,
    'N30',
    'MAIN',
    CASE WHEN t.Num <= 60 THEN 0 ELSE 1 END,
    0,
    0.00,
    'ENU',
    'John Connor'
FROM Tally150 t;

-- 3.7 Order Details (OrderDtl)
-- Line 1 across all orders
INSERT INTO Erp.OrderDtl (Company, OrderNum, OrderLine, PartNum, LineDesc, OrderQty, SellingQuantity, SalesUM, UnitPrice, DocUnitPrice, DspUnitPrice, OpenLine, VoidLine, NeedByDate, RequestDate, FabricationNotes_c)
SELECT 
    h.Company,
    h.OrderNum,
    1,
    CASE (h.OrderNum % 5)
        WHEN 0 THEN 'PART-100'
        WHEN 1 THEN 'PART-200'
        WHEN 2 THEN 'PART-300'
        WHEN 3 THEN 'SUB-01'
        ELSE 'WIDGET-01'
    END,
    'Standard Machined Bracket Line 1',
    CASE 
        WHEN (h.OrderNum BETWEEN 10101 AND 10110) OR (h.OrderNum BETWEEN 20101 AND 20110) THEN 20.0000
        ELSE 10.0000
    END,
    CASE 
        WHEN (h.OrderNum BETWEEN 10101 AND 10110) OR (h.OrderNum BETWEEN 20101 AND 20110) THEN 20.0000
        ELSE 10.0000
    END,
    'EA',
    50.00000,
    50.00000,
    50.00000,
    -- OpenLine: 0 when all releases are fulfilled; 1 if any release remains open (including partial lines with open balance)
    CASE 
        WHEN (h.OrderNum BETWEEN 10001 AND 10060) OR (h.OrderNum BETWEEN 20001 AND 20060) THEN 0
        WHEN (h.OrderNum BETWEEN 10076 AND 10080) OR (h.OrderNum BETWEEN 20076 AND 20080) THEN 1 -- Release 2 open -> line open
        WHEN (h.OrderNum BETWEEN 10061 AND 10100) OR (h.OrderNum BETWEEN 20061 AND 20100) THEN 0 -- Line 1 fully fulfilled
        ELSE 1 -- fully open orders
    END,
    0,
    h.NeedByDate,
    h.RequestDate,
    'Standard quality inspection'
FROM Erp.OrderHed h;

-- Line 2 across partly shipped and selected open orders
INSERT INTO Erp.OrderDtl (Company, OrderNum, OrderLine, PartNum, LineDesc, OrderQty, SellingQuantity, SalesUM, UnitPrice, DocUnitPrice, DspUnitPrice, OpenLine, VoidLine, NeedByDate, RequestDate, FabricationNotes_c)
SELECT 
    h.Company,
    h.OrderNum,
    2,
    CASE WHEN h.Company = 'MFG01' THEN 'MFG1-SPECIAL-01' ELSE 'MFG2-CUSTOM-01' END,
    'Secondary Precision Line 2',
    CASE 
        WHEN (h.OrderNum BETWEEN 10061 AND 10070) OR (h.OrderNum BETWEEN 20061 AND 20070) THEN 15.0000
        ELSE 5.0000
    END,
    CASE 
        WHEN (h.OrderNum BETWEEN 10061 AND 10070) OR (h.OrderNum BETWEEN 20061 AND 20070) THEN 15.0000
        ELSE 5.0000
    END,
    'EA',
    75.00000,
    75.00000,
    75.00000,
    1,
    0,
    h.NeedByDate,
    h.RequestDate,
    'Special surface treatment required'
FROM Erp.OrderHed h
WHERE ((h.OrderNum BETWEEN 10061 AND 10100) OR (h.OrderNum BETWEEN 20061 AND 20100))
   OR (((h.OrderNum BETWEEN 10101 AND 10150) OR (h.OrderNum BETWEEN 20101 AND 20150)) AND (h.OrderNum % 2 = 0));

-- Update OrderAmt to exact sum of line totals (W1)
UPDATE h
SET h.OrderAmt = totals.LineTotal
FROM Erp.OrderHed h
JOIN (
    SELECT Company, OrderNum, SUM(CAST(OrderQty * UnitPrice AS DECIMAL(15, 2))) AS LineTotal
    FROM Erp.OrderDtl
    GROUP BY Company, OrderNum
) totals ON totals.Company = h.Company AND totals.OrderNum = h.OrderNum;

-- 3.8 Order Releases (OrderRel)
-- Split-delivery schedule on selected lines (2 releases: 5.0 fulfilled, 5.0 open)
INSERT INTO Erp.OrderRel (Company, OrderNum, OrderLine, OrderRelNum, OurReqQty, SellingReqQty, ShipToNum, ShipToCustNum, NeedByDate, ReqDate, OpenRelease, FirmRelease, Plant, WarehouseCode)
SELECT d.Company, d.OrderNum, 1, 1, 5.0000, 5.0000, 'MAIN', h.CustNum, DATEADD(day, -5, d.NeedByDate), DATEADD(day, -5, d.RequestDate), 0, 1, CASE WHEN d.Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END, 'MAIN'
FROM Erp.OrderDtl d JOIN Erp.OrderHed h ON h.Company = d.Company AND h.OrderNum = d.OrderNum
WHERE d.OrderLine = 1 AND ((d.OrderNum BETWEEN 10076 AND 10080) OR (d.OrderNum BETWEEN 20076 AND 20080))
UNION ALL
SELECT d.Company, d.OrderNum, 1, 2, 5.0000, 5.0000, 'MAIN', h.CustNum, d.NeedByDate, d.RequestDate, 1, 1, CASE WHEN d.Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END, 'MAIN'
FROM Erp.OrderDtl d JOIN Erp.OrderHed h ON h.Company = d.Company AND h.OrderNum = d.OrderNum
WHERE d.OrderLine = 1 AND ((d.OrderNum BETWEEN 10076 AND 10080) OR (d.OrderNum BETWEEN 20076 AND 20080));

-- Staggered future delivery schedule on selected lines (3 releases: 5.0 each, all open)
INSERT INTO Erp.OrderRel (Company, OrderNum, OrderLine, OrderRelNum, OurReqQty, SellingReqQty, ShipToNum, ShipToCustNum, NeedByDate, ReqDate, OpenRelease, FirmRelease, Plant, WarehouseCode)
SELECT d.Company, d.OrderNum, 2, 1, 5.0000, 5.0000, 'MAIN', h.CustNum, DATEADD(day, -7, d.NeedByDate), DATEADD(day, -7, d.RequestDate), 1, 1, CASE WHEN d.Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END, 'MAIN'
FROM Erp.OrderDtl d JOIN Erp.OrderHed h ON h.Company = d.Company AND h.OrderNum = d.OrderNum
WHERE d.OrderLine = 2 AND ((d.OrderNum BETWEEN 10061 AND 10070) OR (d.OrderNum BETWEEN 20061 AND 20070))
UNION ALL
SELECT d.Company, d.OrderNum, 2, 2, 5.0000, 5.0000, 'MAIN', h.CustNum, d.NeedByDate, d.RequestDate, 1, 1, CASE WHEN d.Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END, 'MAIN'
FROM Erp.OrderDtl d JOIN Erp.OrderHed h ON h.Company = d.Company AND h.OrderNum = d.OrderNum
WHERE d.OrderLine = 2 AND ((d.OrderNum BETWEEN 10061 AND 10070) OR (d.OrderNum BETWEEN 20061 AND 20070))
UNION ALL
SELECT d.Company, d.OrderNum, 2, 3, 5.0000, 5.0000, 'MAIN', h.CustNum, DATEADD(day, 14, d.NeedByDate), DATEADD(day, 14, d.RequestDate), 1, 1, CASE WHEN d.Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END, 'MAIN'
FROM Erp.OrderDtl d JOIN Erp.OrderHed h ON h.Company = d.Company AND h.OrderNum = d.OrderNum
WHERE d.OrderLine = 2 AND ((d.OrderNum BETWEEN 10061 AND 10070) OR (d.OrderNum BETWEEN 20061 AND 20070));

-- Multi-release delivery schedule on selected open lines (2 releases: 10.0 each, all open)
INSERT INTO Erp.OrderRel (Company, OrderNum, OrderLine, OrderRelNum, OurReqQty, SellingReqQty, ShipToNum, ShipToCustNum, NeedByDate, ReqDate, OpenRelease, FirmRelease, Plant, WarehouseCode)
SELECT d.Company, d.OrderNum, 1, 1, 10.0000, 10.0000, 'MAIN', h.CustNum, DATEADD(day, -7, d.NeedByDate), DATEADD(day, -7, d.RequestDate), 1, 1, CASE WHEN d.Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END, 'MAIN'
FROM Erp.OrderDtl d JOIN Erp.OrderHed h ON h.Company = d.Company AND h.OrderNum = d.OrderNum
WHERE d.OrderLine = 1 AND ((d.OrderNum BETWEEN 10101 AND 10110) OR (d.OrderNum BETWEEN 20101 AND 20110))
UNION ALL
SELECT d.Company, d.OrderNum, 1, 2, 10.0000, 10.0000, 'MAIN', h.CustNum, d.NeedByDate, d.RequestDate, 1, 1, CASE WHEN d.Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END, 'MAIN'
FROM Erp.OrderDtl d JOIN Erp.OrderHed h ON h.Company = d.Company AND h.OrderNum = d.OrderNum
WHERE d.OrderLine = 1 AND ((d.OrderNum BETWEEN 10101 AND 10110) OR (d.OrderNum BETWEEN 20101 AND 20110));

-- Single release for all remaining order lines
INSERT INTO Erp.OrderRel (Company, OrderNum, OrderLine, OrderRelNum, OurReqQty, SellingReqQty, ShipToNum, ShipToCustNum, NeedByDate, ReqDate, OpenRelease, FirmRelease, Plant, WarehouseCode)
SELECT 
    d.Company,
    d.OrderNum,
    d.OrderLine,
    1,
    d.OrderQty,
    d.SellingQuantity,
    'MAIN',
    h.CustNum,
    d.NeedByDate,
    d.RequestDate,
    d.OpenLine,
    1,
    CASE WHEN d.Company = 'MFG01' THEN 'MfgSys' ELSE 'Main' END,
    'MAIN'
FROM Erp.OrderDtl d
JOIN Erp.OrderHed h ON h.Company = d.Company AND h.OrderNum = d.OrderNum
WHERE NOT (d.OrderLine = 1 AND ((d.OrderNum BETWEEN 10076 AND 10080) OR (d.OrderNum BETWEEN 20076 AND 20080)))
  AND NOT (d.OrderLine = 2 AND ((d.OrderNum BETWEEN 10061 AND 10070) OR (d.OrderNum BETWEEN 20061 AND 20070)))
  AND NOT (d.OrderLine = 1 AND ((d.OrderNum BETWEEN 10101 AND 10110) OR (d.OrderNum BETWEEN 20101 AND 20110)));

-- 3.9 Shipments (100 shipments per company)
-- MFG01 Shipments (PackNum 50001 to 50100)
INSERT INTO Erp.ShipHead (Company, PackNum, CustNum, ShipDate, ShipToNum, ShipToCustNum, ShipStatus, TrackingNumber, ShipViaCode, Weight, RptLanguageID, CarrierTrackingUrl_c)
SELECT 
    'MFG01',
    50000 + (h.OrderNum - 10000),
    h.CustNum,
    DATEADD(day, 2, h.OrderDate),
    h.ShipToNum,
    h.CustNum,
    'SHIPPED',
    'TRK-M1-' + RIGHT('000000' + CAST(h.OrderNum AS VARCHAR(10)), 6),
    'UPSG',
    CAST(25.0000 + ((h.OrderNum % 10) * 5.2500) AS DECIMAL(15, 4)),
    'ENU',
    'https://track.mockcarrier.internal/m1/' + CAST(h.OrderNum AS VARCHAR(10))
FROM Erp.OrderHed h
WHERE h.Company = 'MFG01' AND h.OrderNum BETWEEN 10001 AND 10100;

-- MFG02 Shipments (PackNum 60001 to 60100)
INSERT INTO Erp.ShipHead (Company, PackNum, CustNum, ShipDate, ShipToNum, ShipToCustNum, ShipStatus, TrackingNumber, ShipViaCode, Weight, RptLanguageID, CarrierTrackingUrl_c)
SELECT 
    'MFG02',
    60000 + (h.OrderNum - 20000),
    h.CustNum,
    DATEADD(day, 2, h.OrderDate),
    h.ShipToNum,
    h.CustNum,
    'SHIPPED',
    'TRK-M2-' + RIGHT('000000' + CAST(h.OrderNum AS VARCHAR(10)), 6),
    'FEDEX',
    CAST(30.0000 + ((h.OrderNum % 10) * 4.5000) AS DECIMAL(15, 4)),
    'ENU',
    'https://track.mockcarrier.internal/m2/' + CAST(h.OrderNum AS VARCHAR(10))
FROM Erp.OrderHed h
WHERE h.Company = 'MFG02' AND h.OrderNum BETWEEN 20001 AND 20100;

-- Shipment Lines (ShipDtl)
-- Ships Line 1 Release 1 for all fulfilled/partly-fulfilled orders:
-- - Orders 10076-10080 / 20076-20080: ships 5.0000 (matching fulfilled Release 1)
-- - All other shipped orders: ships full line quantity 10.0000
INSERT INTO Erp.ShipDtl (Company, PackNum, PackLine, OrderNum, OrderLine, OrderRelNum, PartNum, LineDesc, OurInventoryShipQty, SellingShippedQty, Packages, IUM, SalesUM, CustPartNum, HeatNumber_c, CertificateOfConformance_c)
SELECT 
    sh.Company,
    sh.PackNum,
    d.OrderLine,
    d.OrderNum,
    d.OrderLine,
    1,
    d.PartNum,
    d.LineDesc,
    CASE 
        WHEN (d.OrderNum BETWEEN 10076 AND 10080) OR (d.OrderNum BETWEEN 20076 AND 20080) THEN 5.0000
        ELSE d.OrderQty
    END,
    CASE 
        WHEN (d.OrderNum BETWEEN 10076 AND 10080) OR (d.OrderNum BETWEEN 20076 AND 20080) THEN 5.0000
        ELSE d.SellingQuantity
    END,
    1,
    d.SalesUM,
    d.SalesUM,
    'CP-' + d.PartNum,
    'HT-' + CAST(sh.PackNum AS VARCHAR(10)),
    1
FROM Erp.ShipHead sh
JOIN Erp.OrderDtl d ON d.Company = sh.Company 
                   AND d.OrderNum = (sh.PackNum - 40000)
WHERE d.OrderLine = 1;

-- 3.10 Customer Invoices (100 invoices per company)
-- MFG01 Invoices (InvoiceNum 90001 to 90100)
INSERT INTO Erp.InvcHead (Company, InvoiceNum, CustNum, InvoiceDate, OrderNum, InvoiceType, InvoiceAmt, TermsCode, OpenInvoice, RptLanguageID, ShipToPONum_c, BillingContact_c)
SELECT 
    'MFG01',
    90000 + (h.OrderNum - 10000),
    h.CustNum,
    DATEADD(day, 4, h.OrderDate),
    h.OrderNum,
    'STD',
    0.00,
    'N30',
    CASE WHEN h.OrderNum <= 10060 THEN 0 ELSE 1 END,
    'ENU',
    h.PONum,
    'acct-payable@mfg01-customer.com'
FROM Erp.OrderHed h
WHERE h.Company = 'MFG01' AND h.OrderNum BETWEEN 10001 AND 10100;

-- MFG02 Invoices (InvoiceNum 80001 to 80100)
INSERT INTO Erp.InvcHead (Company, InvoiceNum, CustNum, InvoiceDate, OrderNum, InvoiceType, InvoiceAmt, TermsCode, OpenInvoice, RptLanguageID, ShipToPONum_c, BillingContact_c)
SELECT 
    'MFG02',
    80000 + (h.OrderNum - 20000),
    h.CustNum,
    DATEADD(day, 4, h.OrderDate),
    h.OrderNum,
    'STD',
    0.00,
    'N30',
    CASE WHEN h.OrderNum <= 20060 THEN 0 ELSE 1 END,
    'ENU',
    h.PONum,
    'acct-payable@mfg02-customer.com'
FROM Erp.OrderHed h
WHERE h.Company = 'MFG02' AND h.OrderNum BETWEEN 20001 AND 20100;

-- Invoice Lines (InvcDtl) matching ShipDtl
INSERT INTO Erp.InvcDtl (Company, InvoiceNum, InvoiceLine, OrderNum, OrderLine, OrderRelNum, PackNum, PackLine, PartNum, LineDesc, SellingShipQty, UnitPrice, DocUnitPrice, ExtPrice, ShipToCustNum, ShipToNum, GLAnalysisCode_c)
SELECT 
    ih.Company,
    ih.InvoiceNum,
    sd.PackLine,
    sd.OrderNum,
    sd.OrderLine,
    sd.OrderRelNum,
    sd.PackNum,
    sd.PackLine,
    sd.PartNum,
    sd.LineDesc,
    sd.SellingShippedQty,
    od.UnitPrice,
    od.DocUnitPrice,
    CAST(sd.SellingShippedQty * od.UnitPrice AS DECIMAL(15, 2)),
    sh.CustNum,
    sh.ShipToNum,
    'REV-MFG'
FROM Erp.InvcHead ih
JOIN Erp.ShipHead sh ON sh.Company = ih.Company 
                     AND sh.PackNum = (CASE WHEN ih.Company = 'MFG01' THEN ih.InvoiceNum - 40000 ELSE ih.InvoiceNum - 20000 END)
JOIN Erp.ShipDtl sd ON sd.Company = sh.Company AND sd.PackNum = sh.PackNum
JOIN Erp.OrderDtl od ON od.Company = sd.Company AND od.OrderNum = sd.OrderNum AND od.OrderLine = sd.OrderLine;

-- Update InvoiceAmt to exact sum of InvcDtl ExtPrice (W1)
UPDATE ih
SET ih.InvoiceAmt = totals.InvcTotal
FROM Erp.InvcHead ih
JOIN (
    SELECT Company, InvoiceNum, SUM(ExtPrice) AS InvcTotal
    FROM Erp.InvcDtl
    GROUP BY Company, InvoiceNum
) totals ON totals.Company = ih.Company AND totals.InvoiceNum = ih.InvoiceNum;
GO

/* =============================================================================
   3.12 Checkpoint 2 Seed Realism Updates (R1, R3, R4, R6)
   ============================================================================= */
-- R1: Customer part numbers on ShipDtl for existing MFG01 packs (50001-50100 have PackLine 1)
UPDATE Erp.ShipDtl
SET CustPartNum = 'CP-8842-A'
WHERE Company = 'MFG01' AND PackNum = 50001 AND PackLine = 1;

UPDATE Erp.ShipDtl
SET CustPartNum = 'CP-9901-B'
WHERE Company = 'MFG01' AND PackNum = 50002 AND PackLine = 1;

-- R6: Shipment total weight on ShipHead for test pack 50001
UPDATE Erp.ShipHead
SET Weight = 48.5000
WHERE Company = 'MFG01' AND PackNum = 50001;

-- R3: Revision number and extended weight on OrderDtl for test order 10061 (orders 10061-10100 have both Line 1 and Line 2)
UPDATE Erp.OrderDtl
SET RevisionNum = 'B', ExtWeight = 45.5000
WHERE Company = 'MFG01' AND OrderNum = 10061 AND OrderLine = 1;

UPDATE Erp.OrderDtl
SET RevisionNum = 'A', ExtWeight = 120.0000
WHERE Company = 'MFG01' AND OrderNum = 10061 AND OrderLine = 2;

-- R4: Ship-to PO (UD column ShipToPONum_c) on InvcHead for test invoice 90001 (MFG01 invoices are 90001-90100)
UPDATE Erp.InvcHead
SET ShipToPONum_c = 'PO-9912'
WHERE Company = 'MFG01' AND InvoiceNum = 90001;
GO

/* =============================================================================
   4. VERIFICATION QUERY (Information only)
   ============================================================================= */
SELECT 'Erp.LabConstants' AS TableName, COUNT(*) AS RowCnt FROM Erp.LabConstants UNION ALL
SELECT 'Erp.Company', COUNT(*) FROM Erp.Company UNION ALL
SELECT 'Erp.Customer', COUNT(*) FROM Erp.Customer UNION ALL
SELECT 'Erp.ShipTo', COUNT(*) FROM Erp.ShipTo UNION ALL
SELECT 'Erp.Part', COUNT(*) FROM Erp.Part UNION ALL
SELECT 'Erp.PartPlant', COUNT(*) FROM Erp.PartPlant UNION ALL
SELECT 'Erp.PartWhse', COUNT(*) FROM Erp.PartWhse UNION ALL
SELECT 'Erp.OrderHed', COUNT(*) FROM Erp.OrderHed UNION ALL
SELECT 'Erp.OrderDtl', COUNT(*) FROM Erp.OrderDtl UNION ALL
SELECT 'Erp.OrderRel', COUNT(*) FROM Erp.OrderRel UNION ALL
SELECT 'Erp.ShipHead', COUNT(*) FROM Erp.ShipHead UNION ALL
SELECT 'Erp.ShipDtl', COUNT(*) FROM Erp.ShipDtl UNION ALL
SELECT 'Erp.InvcHead', COUNT(*) FROM Erp.InvcHead UNION ALL
SELECT 'Erp.InvcDtl', COUNT(*) FROM Erp.InvcDtl;
GO
