# Lab B01: MFG01 Net-30 Customer Directory (Single-Table)

## Partner Ticket

| Field | Value |
|---|---|
| **Ticket ID** | `KIN-BAQ-201` |
| **Client** | MFG01 Manufacturing Corp |
| **BAQ ID** | `BAQ_B01_CustDirectory` |
| **Category** | Build Drill — Single-Table |
| **Environment** | SQL Server 2016 (`[ErpLab].[Erp].*`) |
| **Starter File** | [`labs/baq/starter/B01.json`](starter/B01.json) |
| **Summary** | Accounts Receivable at MFG01 needs a customer directory BAQ (`BAQ_B01_CustDirectory`) on `Erp.Customer` listing all customers in company `MFG01` whose payment terms (`TermsCode`) are `'N30'`, including their assigned account manager (`AccountManager_c`). |

### Acceptance Criteria
1. Query table `Erp.Customer` filtered to `Company = 'MFG01'` and `TermsCode = 'N30'`.
2. Include display fields in order: `Customer.Company`, `Customer.CustNum`, `Customer.CustID`, `Customer.Name`, `Customer.City`, `Customer.State`, `Customer.TermsCode`, `Customer.AccountManager_c` (`[B18]`).
3. Sort results by `Customer.CustNum ASC`.

> **Banners & Citations**
> - **Reference**: [`docs/reference/02-baq.md`](../../docs/reference/02-baq.md) (`[B2, B7, B8, B9, B11, B12, B17, B18]`), [`docs/reference/decisions.md`](../../docs/reference/decisions.md), and [`sql/00-README.md`](../../sql/00-README.md).
> - **Default chosen for the lab, not confirmed against Epicor.**

---

## Workflow & CLI Commands

```bash
# 1. Inspect and edit your working copy of the starter BAQ JSON
cp labs/baq/starter/B01.json /tmp/B01.json

# 2. Compile the BAQ to SQL Server 2016 T-SQL
engines/baq/baq compile /tmp/B01.json

# 3. On the SQL Server 2016 VM, execute or grade the BAQ
engines/baq/baq run /tmp/B01.json
```
