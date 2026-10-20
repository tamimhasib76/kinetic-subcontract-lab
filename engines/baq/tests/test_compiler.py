"""Unit tests for the BAQ compiler, validator, CLI, and grader (no database required)."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from engines.baq.cli import main as cli_main
from engines.baq.compiler import compile_baq, compile_baq_file
from engines.baq.grader import grade_baq, grade_rows
from engines.baq.schema import BANNER, BAQValidationError, validate_baq

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


class TestBAQCompiler(unittest.TestCase):
    """Compiler unit tests that verify generated T-SQL text without a database."""

    def test_compile_open_orders_example(self) -> None:
        sql = compile_baq_file(EXAMPLES_DIR / "open_orders.json", include_header=False)
        expected = """\
SELECT
    [Customer].[CustID] AS [Customer_CustID],
    [Customer].[Name] AS [Customer_Name],
    [OrderHed].[Company] AS [OrderHed_Company],
    [OrderHed].[OrderNum] AS [OrderHed_OrderNum],
    [OrderHed].[CustNum] AS [OrderHed_CustNum],
    [OrderHed].[OrderDate] AS [OrderHed_OrderDate],
    [OrderHed].[NeedByDate] AS [OrderHed_NeedByDate],
    [OrderDtl].[OrderLine] AS [OrderDtl_OrderLine],
    [OrderDtl].[PartNum] AS [OrderDtl_PartNum],
    [OrderDtl].[OrderQty] AS [OrderDtl_OrderQty],
    [OrderDtl].[UnitPrice] AS [OrderDtl_UnitPrice],
    DATEDIFF(day, [OrderHed].[NeedByDate], (SELECT [ConstantDate] FROM [ErpLab].[Erp].[LabConstants] WHERE [ConstantName] = N'FixedLabDate')) AS [Calculated_DaysLate]
FROM [ErpLab].[Erp].[OrderHed] AS [OrderHed]
INNER JOIN [ErpLab].[Erp].[OrderDtl] AS [OrderDtl]
    ON [OrderHed].[Company] = [OrderDtl].[Company]
   AND [OrderHed].[OrderNum] = [OrderDtl].[OrderNum]
INNER JOIN [ErpLab].[Erp].[Customer] AS [Customer]
    ON [OrderHed].[Company] = [Customer].[Company]
   AND [OrderHed].[CustNum] = [Customer].[CustNum]
WHERE [OrderHed].[Company] = N'MFG01'
  AND [OrderHed].[OpenOrder] = 1
  AND [OrderHed].[VoidOrder] = 0
  AND [OrderDtl].[OpenLine] = 1
  AND [OrderDtl].[VoidLine] = 0
ORDER BY [OrderHed].[OrderNum] ASC, [OrderDtl].[OrderLine] ASC;"""
        self.assertEqual(sql, expected)

    def test_header_includes_required_banner(self) -> None:
        sql_with_header = compile_baq_file(EXAMPLES_DIR / "open_orders.json", include_header=True)
        self.assertIn(f"-- Banner: {BANNER}", sql_with_header)
        self.assertIn("-- Target: Microsoft SQL Server 2016+ ([ErpLab].[Erp].*)", sql_with_header)

    def test_compile_inner_subquery_example(self) -> None:
        sql = compile_baq_file(EXAMPLES_DIR / "order_rel_summary.json", include_header=False)
        expected = """\
SELECT
    [Part].[Company] AS [Part_Company],
    [Part].[PartNum] AS [Part_PartNum],
    [Part].[PartDescription] AS [Part_PartDescription],
    [WhseSub].[WhseCount] AS [WhseSub_WhseCount],
    [WhseSub].[TotalOnHand] AS [WhseSub_TotalOnHand]
FROM [ErpLab].[Erp].[Part] AS [Part]
LEFT OUTER JOIN (
    SELECT
        [PartWhse].[Company] AS [Company],
        [PartWhse].[PartNum] AS [PartNum],
        COUNT([PartWhse].[WarehouseCode]) AS [WhseCount],
        SUM([PartWhse].[OnHandQty]) AS [TotalOnHand]
    FROM [ErpLab].[Erp].[PartWhse] AS [PartWhse]
    GROUP BY [PartWhse].[Company], [PartWhse].[PartNum]
) AS [WhseSub]
    ON [Part].[Company] = [WhseSub].[Company]
   AND [Part].[PartNum] = [WhseSub].[PartNum]
WHERE [Part].[Company] = N'MFG01'
ORDER BY [Part].[PartNum] ASC;"""
        self.assertEqual(sql, expected)

    def test_single_table_select_and_distinct(self) -> None:
        baq = {
            "baqId": "SingleTableDistinct",
            "distinct": True,
            "tables": ["Part"],
            "displayFields": [
                {"table": "Part", "field": "Company"},
                {"table": "Part", "field": "ClassID"},
            ],
            "orderBy": [{"table": "Part", "field": "ClassID", "direction": "DESC"}],
        }
        sql = compile_baq(baq, include_header=False)
        expected = """\
SELECT DISTINCT
    [Part].[Company] AS [Part_Company],
    [Part].[ClassID] AS [Part_ClassID]
FROM [ErpLab].[Erp].[Part] AS [Part]
ORDER BY [Part].[ClassID] DESC;"""
        self.assertEqual(sql, expected)

    def test_left_outer_join_with_custom_table_alias(self) -> None:
        baq = {
            "baqId": "LeftJoinAliasTest",
            "tables": [
                {"table": "Customer", "alias": "Cust"},
                {"table": "ShipTo", "alias": "ST"},
            ],
            "relations": [
                {
                    "parentTable": "Cust",
                    "childTable": "ST",
                    "joinType": "left outer",
                    "fields": [
                        {"parentField": "Company", "childField": "Company"},
                        {"parentField": "CustNum", "childField": "CustNum"},
                    ],
                }
            ],
            "displayFields": [
                {"table": "Cust", "field": "CustID"},
                {"table": "ST", "field": "ShipToNum"},
            ],
        }
        sql = compile_baq(baq, include_header=False)
        self.assertIn("LEFT OUTER JOIN [ErpLab].[Erp].[ShipTo] AS [ST]", sql)
        self.assertIn("[Cust].[CustID] AS [Cust_CustID]", sql)
        self.assertIn("[ST].[ShipToNum] AS [ST_ShipToNum]", sql)

    def test_calculated_field_case_isnull_and_convert(self) -> None:
        baq = {
            "baqId": "CalcExprTest",
            "tables": ["Part"],
            "displayFields": [{"table": "Part", "field": "PartNum"}],
            "calculatedFields": [
                {
                    "name": "PriceTier",
                    "dataType": "nvarchar",
                    "expression": "CASE WHEN ISNULL([Part].[UnitPrice], 0) >= 50 THEN N'High' ELSE N'Standard' END",
                },
                {
                    "name": "RoundedPrice",
                    "dataType": "int",
                    "expression": "CONVERT(int, [Part].[UnitPrice])",
                },
            ],
        }
        sql = compile_baq(baq, include_header=False)
        self.assertIn(
            "CASE WHEN ISNULL([Part].[UnitPrice], 0) >= 50 THEN N'High' ELSE N'Standard' END AS [Calculated_PriceTier]",
            sql,
        )
        self.assertIn("CONVERT(int, [Part].[UnitPrice]) AS [Calculated_RoundedPrice]", sql)

    def test_group_by_with_aggregates_on_top_level(self) -> None:
        baq = {
            "baqId": "TopLevelAggTest",
            "tables": ["InvcDtl"],
            "displayFields": [
                {"table": "InvcDtl", "field": "Company", "groupBy": True},
                {"table": "InvcDtl", "field": "InvoiceNum", "groupBy": True},
                {"table": "InvcDtl", "field": "ExtPrice", "aggregate": "SUM", "alias": "TotalExtPrice"},
            ],
        }
        sql = compile_baq(baq, include_header=False)
        self.assertIn("SUM([InvcDtl].[ExtPrice]) AS [TotalExtPrice]", sql)
        self.assertIn("GROUP BY [InvcDtl].[Company], [InvcDtl].[InvoiceNum]", sql)

    def test_order_by_calculated_field_name(self) -> None:
        baq = {
            "baqId": "OrderByCalcTest",
            "tables": ["OrderDtl"],
            "displayFields": [{"table": "OrderDtl", "field": "OrderNum"}],
            "calculatedFields": [
                {
                    "name": "LineAmount",
                    "dataType": "decimal",
                    "expression": "[OrderDtl].[OrderQty] * [OrderDtl].[UnitPrice]",
                }
            ],
            "orderBy": [{"field": "LineAmount", "direction": "DESC"}],
        }
        sql = compile_baq(baq, include_header=False)
        self.assertTrue(sql.endswith("ORDER BY [Calculated_LineAmount] DESC;"), msg=sql)

    def test_criteria_operators_in_between_null_like_or(self) -> None:
        baq = {
            "baqId": "CriteriaOperatorsTest",
            "tables": ["OrderHed"],
            "displayFields": [{"table": "OrderHed", "field": "OrderNum"}],
            "tableCriteria": [
                {"table": "OrderHed", "field": "Company", "operator": "IN", "value": ["MFG01", "MFG02"]},
                {
                    "table": "OrderHed",
                    "field": "OrderNum",
                    "operator": "BETWEEN",
                    "value": [10001, 10050],
                    "conjunction": "AND",
                },
                {"table": "OrderHed", "field": "PONum", "operator": "IS NOT NULL", "conjunction": "AND"},
                {"table": "OrderHed", "field": "TermsCode", "operator": "LIKE", "value": "N%", "conjunction": "OR"},
                {
                    "table": "OrderHed",
                    "field": "NeedByDate",
                    "operator": "<=",
                    "otherTable": "OrderHed",
                    "otherField": "RequestDate",
                    "conjunction": "AND",
                },
            ],
        }
        sql = compile_baq(baq, include_header=False)
        expected_where = """\
WHERE [OrderHed].[Company] IN (N'MFG01', N'MFG02')
  AND [OrderHed].[OrderNum] BETWEEN 10001 AND 10050
  AND [OrderHed].[PONum] IS NOT NULL
  OR [OrderHed].[TermsCode] LIKE N'N%'
  AND [OrderHed].[NeedByDate] <= [OrderHed].[RequestDate];"""
        self.assertTrue(sql.endswith(expected_where), msg=sql)

    def test_rejects_cte_union_and_parameters(self) -> None:
        for bad_type in ("CTE", "RecursiveCTE", "Union", "UnionAll", "Intersect", "Except"):
            with self.subTest(subquery_type=bad_type):
                with self.assertRaises(BAQValidationError):
                    validate_baq(
                        {
                            "baqId": "BadType",
                            "subqueries": [
                                {
                                    "name": "SQ1",
                                    "type": bad_type,
                                    "tables": ["OrderHed"],
                                    "displayFields": [{"table": "OrderHed", "field": "OrderNum"}],
                                }
                            ],
                        }
                    )

        # Reject @Parameter in criterion
        with self.assertRaises(BAQValidationError):
            validate_baq(
                {
                    "baqId": "BadParam",
                    "tables": ["Customer"],
                    "displayFields": [{"table": "Customer", "field": "CustID"}],
                    "criteria": [{"table": "Customer", "field": "Name", "operator": "=", "value": "@IDP_FullName"}],
                }
            )

        # Reject @Parameter in calculated field
        with self.assertRaises(BAQValidationError):
            validate_baq(
                {
                    "baqId": "BadCalcParam",
                    "tables": ["Customer"],
                    "displayFields": [{"table": "Customer", "field": "CustID"}],
                    "calculatedFields": [
                        {"name": "Filtered", "dataType": "nvarchar", "expression": "ISNULL(@CustParam, N'')"}
                    ],
                }
            )

    def test_rejects_select_or_trailing_as_alias_in_calculated_field(self) -> None:
        # Reject leading SELECT
        with self.assertRaises(BAQValidationError):
            validate_baq(
                {
                    "baqId": "BadSelectCalc",
                    "tables": ["OrderHed"],
                    "calculatedFields": [
                        {"name": "Bad", "dataType": "int", "expression": "SELECT COUNT(*) FROM Erp.OrderHed"}
                    ],
                }
            )

        # Reject trailing AS <alias> per [B12]
        with self.assertRaises(BAQValidationError):
            validate_baq(
                {
                    "baqId": "BadAliasCalc",
                    "tables": ["OrderHed"],
                    "calculatedFields": [
                        {
                            "name": "BadAlias",
                            "dataType": "nvarchar",
                            "expression": "STRING_AGG(CASE WHEN [OrderHed].[OpenOrder] = 1 THEN N'Open' END, N', ') AS OpenList",
                        }
                    ],
                }
            )

        # Allow STRING_AGG with nested CASE when no trailing AS <alias> is present ([B12])
        valid = validate_baq(
            {
                "baqId": "GoodStringAgg",
                "tables": ["OrderHed"],
                "calculatedFields": [
                    {
                        "name": "OpenList",
                        "dataType": "nvarchar",
                        "expression": "STRING_AGG(CASE WHEN [OrderHed].[OpenOrder] = 1 THEN N'Open' END, N', ')",
                    }
                ],
            }
        )
        sql = compile_baq(valid, include_header=False)
        self.assertIn(
            "STRING_AGG(CASE WHEN [OrderHed].[OpenOrder] = 1 THEN N'Open' END, N', ') AS [Calculated_OpenList]",
            sql,
        )

    def test_schema_tables_json_matches_sql_ddl(self) -> None:
        import json
        from engines.baq.schema import load_erp_schema, parse_schema_sql

        repo_root = Path(__file__).resolve().parents[3]
        sql_path = repo_root / "sql" / "01-erp-app-schema.sql"
        json_path = Path(__file__).resolve().parents[1] / "schema-tables.json"

        parsed_from_sql = parse_schema_sql(sql_path)
        loaded_from_json = json.loads(json_path.read_text(encoding="utf-8"))["tables"]
        self.assertEqual(parsed_from_sql, loaded_from_json)

        erp_schema = load_erp_schema()
        self.assertEqual(set(erp_schema.keys()), set(parsed_from_sql.keys()))

    def test_rejects_nonexistent_table_in_erplab_erp(self) -> None:
        for bad_table in ("Vendor", "POHeader", "PODetail", "PORel", "NonExistentTable"):
            with self.subTest(table=bad_table):
                with self.assertRaises(BAQValidationError) as ctx:
                    compile_baq(
                        {
                            "baqId": "BadTableBAQ",
                            "tables": [bad_table],
                            "displayFields": [{"table": bad_table, "field": "Company"}],
                        }
                    )
                self.assertIn(bad_table, str(ctx.exception))

        # Also verify `baq compile` CLI fails with exit code 2 on a nonexistent table
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad_table.json"
            bad_file.write_text(
                '{"baqId": "BadCLI", "tables": ["Vendor"], "displayFields": [{"table": "Vendor", "field": "Company"}]}',
                encoding="utf-8",
            )
            err_buf = io.StringIO()
            with redirect_stderr(err_buf):
                rc = cli_main(["compile", str(bad_file)])
            self.assertEqual(rc, 2)
            self.assertIn("Vendor", err_buf.getvalue())

    def test_rejects_nonexistent_columns_across_all_clauses(self) -> None:
        # 1. Display field column does not exist
        with self.assertRaises(BAQValidationError):
            compile_baq(
                {
                    "baqId": "BadDisplayCol",
                    "tables": ["Part"],
                    "displayFields": [{"table": "Part", "field": "InActive"}],
                }
            )

        # 2. Relation join column does not exist
        with self.assertRaises(BAQValidationError):
            compile_baq(
                {
                    "baqId": "BadJoinCol",
                    "tables": ["OrderHed", "Customer"],
                    "relations": [
                        {
                            "parentTable": "OrderHed",
                            "childTable": "Customer",
                            "joinType": "inner",
                            "fields": [
                                {"parentField": "Company", "childField": "Company"},
                                {"parentField": "BadCustKey", "childField": "CustNum"},
                            ],
                        }
                    ],
                    "displayFields": [{"table": "OrderHed", "field": "OrderNum"}],
                }
            )

        # 3. Criterion column does not exist
        with self.assertRaises(BAQValidationError):
            compile_baq(
                {
                    "baqId": "BadCriteriaCol",
                    "tables": ["OrderDtl"],
                    "displayFields": [{"table": "OrderDtl", "field": "OrderNum"}],
                    "tableCriteria": [
                        {"table": "OrderDtl", "field": "DiscountPercent", "operator": ">", "value": 0}
                    ],
                }
            )

        # 4. Calculated field expression references nonexistent column (qualified and unqualified)
        with self.assertRaises(BAQValidationError):
            compile_baq(
                {
                    "baqId": "BadCalcColQualified",
                    "tables": ["OrderDtl"],
                    "displayFields": [{"table": "OrderDtl", "field": "OrderNum"}],
                    "calculatedFields": [
                        {
                            "name": "NetAmt",
                            "dataType": "decimal",
                            "expression": "[OrderDtl].[OrderQty] * [OrderDtl].[UnitPrice] - [OrderDtl].[Discount]",
                        }
                    ],
                }
            )

        with self.assertRaises(BAQValidationError):
            compile_baq(
                {
                    "baqId": "BadCalcColUnqualified",
                    "tables": ["OrderDtl"],
                    "displayFields": [{"table": "OrderDtl", "field": "OrderNum"}],
                    "calculatedFields": [
                        {
                            "name": "BadExpr",
                            "dataType": "decimal",
                            "expression": "OrderQty * NonExistentPriceCol",
                        }
                    ],
                }
            )

        # 5. OrderBy column does not exist
        with self.assertRaises(BAQValidationError):
            compile_baq(
                {
                    "baqId": "BadOrderByCol",
                    "tables": ["Customer"],
                    "displayFields": [{"table": "Customer", "field": "CustID"}],
                    "orderBy": [{"table": "Customer", "field": "CreditLimit", "direction": "DESC"}],
                }
            )

        # 6. InnerSubQuery column referenced in TopLevel when not exposed by InnerSubQuery
        with self.assertRaises(BAQValidationError):
            compile_baq(
                {
                    "baqId": "BadSubqueryCol",
                    "subqueries": [
                        {
                            "name": "Sub",
                            "type": "InnerSubQuery",
                            "tables": ["PartWhse"],
                            "displayFields": [
                                {"table": "PartWhse", "field": "Company", "groupBy": True},
                                {"table": "PartWhse", "field": "PartNum", "groupBy": True},
                            ],
                        },
                        {
                            "name": "TopLevel",
                            "type": "TopLevel",
                            "tables": ["Part", {"table": "Sub", "isSubQuery": True}],
                            "relations": [
                                {
                                    "parentTable": "Part",
                                    "childTable": "Sub",
                                    "joinType": "inner",
                                    "fields": [
                                        {"parentField": "Company", "childField": "Company"},
                                        {"parentField": "PartNum", "childField": "PartNum"},
                                    ],
                                }
                            ],
                            "displayFields": [
                                {"table": "Part", "field": "PartNum"},
                                {"table": "Sub", "field": "OnHandQty"},
                            ],
                        },
                    ],
                }
            )


class TestBAQGraderAndCLI(unittest.TestCase):
    """Unit tests for the grader and CLI commands without needing a SQL Server instance."""

    def test_grader_passes_matching_results_and_reports_differences(self) -> None:
        expected_cols = ["OrderHed_Company", "OrderHed_OrderNum", "Calculated_LineTotal"]
        expected_rows = [
            {"OrderHed_Company": "MFG01", "OrderHed_OrderNum": "10001", "Calculated_LineTotal": "500.00"},
            {"OrderHed_Company": "MFG01", "OrderHed_OrderNum": "10002", "Calculated_LineTotal": "250.50"},
        ]

        # Exact match (even with trailing zero difference 250.5 vs 250.50)
        actual_ok = [
            {"OrderHed_Company": "MFG01", "OrderHed_OrderNum": "10002", "Calculated_LineTotal": "250.5"},
            {"OrderHed_Company": "MFG01", "OrderHed_OrderNum": "10001", "Calculated_LineTotal": "500.0000"},
        ]
        res_ok = grade_rows(expected_cols, actual_ok, expected_cols, expected_rows)
        self.assertTrue(res_ok.passed, msg=res_ok.summary())

        # Cell value difference
        actual_diff = [
            {"OrderHed_Company": "MFG01", "OrderHed_OrderNum": "10001", "Calculated_LineTotal": "100.00"},
            {"OrderHed_Company": "MFG01", "OrderHed_OrderNum": "10002", "Calculated_LineTotal": "250.50"},
        ]
        res_diff = grade_rows(expected_cols, actual_diff, expected_cols, expected_rows)
        self.assertFalse(res_diff.passed)
        self.assertEqual(len(res_diff.mismatches), 1)

        # Row count difference
        actual_extra = expected_rows + [
            {"OrderHed_Company": "MFG01", "OrderHed_OrderNum": "10003", "Calculated_LineTotal": "500.00"}
        ]
        res_extra = grade_rows(expected_cols, actual_extra, expected_cols, expected_rows)
        self.assertFalse(res_extra.passed)
        self.assertEqual(res_extra.actual_row_count, 3)

    def test_cli_compile_and_grade(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(["compile", "--no-header", str(EXAMPLES_DIR / "open_orders.json")])
        self.assertEqual(rc, 0)
        self.assertIn("FROM [ErpLab].[Erp].[OrderHed] AS [OrderHed]", buf.getvalue())

        # Test `baq grade` with CSV files and mock DB connection
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            exp_csv = tmp / "expected.csv"
            act_csv = tmp / "actual.csv"
            csv_content = "OrderHed_Company,OrderHed_OrderNum\nMFG01,10001\n"
            exp_csv.write_text(csv_content, encoding="utf-8")
            act_csv.write_text(csv_content, encoding="utf-8")

            out_buf = io.StringIO()
            with redirect_stdout(out_buf):
                rc_grade = cli_main(["grade", str(act_csv), str(exp_csv)])
            self.assertEqual(rc_grade, 0)
            self.assertIn("Grade: PASS", out_buf.getvalue())

            # Test `baq grade` with a mock pyodbc connection on a JSON BAQ
            class MockCursor:
                description = [("OrderHed_Company",), ("OrderHed_OrderNum",)]

                def execute(self, sql: str) -> None:
                    self.last_sql = sql

                def fetchall(self) -> list[tuple[str, int]]:
                    return [("MFG01", 10001)]

            class MockConnection:
                def cursor(self) -> MockCursor:
                    return MockCursor()

            baq_def = {
                "baqId": "SimpleTest",
                "tables": ["OrderHed"],
                "displayFields": [
                    {"table": "OrderHed", "field": "Company"},
                    {"table": "OrderHed", "field": "OrderNum"},
                ],
            }
            res = grade_baq(baq_def, exp_csv, connection=MockConnection())
            self.assertTrue(res.passed)

            # Test `make_expected.py` (`generate_expected_csvs`) with mock connection
            from engines.baq.make_expected import generate_expected_csvs

            ans_dir = tmp / "answers"
            exp_out_dir = tmp / "expected_out"
            ans_dir.mkdir()
            import json

            (ans_dir / "B01.json").write_text(json.dumps(baq_def), encoding="utf-8")
            generated = generate_expected_csvs(
                answers_dir=ans_dir,
                expected_dir=exp_out_dir,
                connection=MockConnection(),
            )
            self.assertEqual(len(generated), 1)
            self.assertEqual(generated[0][0], "B01")
            self.assertEqual(generated[0][2], 1)
            self.assertEqual((exp_out_dir / "B01.csv").read_text(encoding="utf-8"), csv_content)

        # Verify `baq run` without connection string env var exits cleanly with error code 2
        err_buf = io.StringIO()
        with redirect_stderr(err_buf):
            rc_run = cli_main(["run", "--env-var", "NONEXISTENT_BAQ_CONN_VAR", str(EXAMPLES_DIR / "open_orders.json")])
        self.assertEqual(rc_run, 2)
        self.assertIn("No SQL Server connection string found", err_buf.getvalue())


if __name__ == "__main__":
    unittest.main()

