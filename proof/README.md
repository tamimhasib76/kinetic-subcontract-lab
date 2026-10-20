# Public Proof Portfolio — Synthetic Lab Case Studies & 5-Minute Demo Scripts

> **Notice**: Lab exercise on synthetic data. Not client work.
> 
> - Every file in this `proof/` folder uses **100% synthetic lab data** (`MFG01`, `MFG02`, `ORCHID`, `PART-200`, `50001`, `10061`).
> - **No SQL Server or SSRS ran in this authoring environment**: only offline Python verification tools ([`dmt-validator/validate_dmt.py`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/dmt-validator/validate_dmt.py) and [`engines/baq/cli.py`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/engines/baq/cli.py)) were executed locally.
> - **Strict Content Hygiene**: This directory shows **only** validator output, HTML reports, and BAQ compiler SQL output. It contains **zero** Epicor screenshots, **zero** logos, **zero** UI chrome, and **zero** raw RDL XML text (`AGENTS.md` Rule 4).
> - **TODO**: PackSlip PDF render: to be produced on the VM.
> - **Required Lab Banner**: *"Default chosen for the lab, not confirmed against Epicor."* applies to every unconfirmed behavior or approved Bucket A lab default ([`docs/reference/decisions.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/docs/reference/decisions.md)).

---

## Contents

### 1. One-Page Case Studies
| # | Case Study | Artifact Shown | Link |
|---|---|---|---|
| **01** | **DMT Pre-Load Cleanup (15 Findings -> 0 Errors)** | `validate_dmt.py` CLI output + HTML remediation report ([`reports/dmt-remediation.html`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/reports/dmt-remediation.html)) | [`case-study-01-dmt-cleanup.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/case-study-01-dmt-cleanup.md) |
| **02** | **Packing Slip (`PackSlip`) RDD + RDL Modification** | Workflow checklist and field mappings (PDF render to be produced on the VM) | [`case-study-02-packslip-rdl-mod.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/case-study-02-packslip-rdl-mod.md) |
| **03** | **BAQ Fix Drills (Multi-Company Join & Integer Division)** | `baq compile` SQL Server 2016 T-SQL output (before vs. after) | [`case-study-03-baq-fix.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/case-study-03-baq-fix.md) |

### 2. Five-Minute Live Demo Scripts
| # | Demo Script | Target Duration | Link |
|---|---| :---: |---|
| **01** | **5-Minute Demo Script: DMT Pre-Load Cleanup** | 5:00 | [`demo-script-01-dmt-cleanup.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/demo-script-01-dmt-cleanup.md) |
| **02** | **5-Minute Demo Script: `PackSlip` RDL Modification** | 5:00 | [`demo-script-02-packslip-rdl-mod.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/demo-script-02-packslip-rdl-mod.md) |
| **03** | **5-Minute Demo Script: BAQ Fix & SQL Compilation** | 5:00 | [`demo-script-03-baq-fix.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/demo-script-03-baq-fix.md) |
