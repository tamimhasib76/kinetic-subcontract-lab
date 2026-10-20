# 5-Minute Demo Script 02: Packing Slip (`PackSlip`) RDD + RDL Modification

> **Notice**: Lab exercise on synthetic data. Not client work.
>
> **Synthetic Lab Disclosure & Environment Notice**: Uses synthetic lab specifications (`MFG01`, `PackNum = 50001`, `TableGuid = a1111111111111111111111111111101`). No SQL Server or SSRS ran on this authoring host; specific render figures and timings are marked `[to be captured on the VM]`. Zero Epicor screenshots, logos, or raw RDL XML text are used.
> **Lab Banner**: *"Default chosen for the lab, not confirmed against Epicor."*

---

## Timing & Pacing Overview (Total: 5:00)

| Segment | Time | Screen / Artifact Shown | Objective |
|---| :---: |---|---|
| **1. Problem & RDD Exclusions** | `0:00 – 1:15` | [`case-study-02-packslip-rdl-mod.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/case-study-02-packslip-rdl-mod.md) | Show why `CustPartNum` and `OrderNum_ProjManager_c` are absent until un-excluded in a duplicated RDD (`[S12, S14, S15, S16]`). |
| **2. Style Copy & No Sync Dataset** | `1:15 – 2:30` | Workflow checklist in Case Study 02 | Explain copying the system Report Style (`[S1, S5, S9]`) and manually editing the dataset query/fields without clicking `Sync Dataset` (`[S24, S25]`). |
| **3. Render Review** | `2:30 – 4:00` | Case Study 02 render section | Review the target layout showing un-excluded `CustPartNum` and linked `OrderNum_ProjManager_c` [renders to be captured on the VM]. |
| **4. Round-Trip Verification** | `4:00 – 5:00` | Round-trip verification steps | Demonstrate the mandatory re-download check (`[S32, S8]`, `01-ssrs-forms.md` §7c) before closing the ticket. |

---

## Minute-by-Minute Script

### `0:00 – 1:15` · 1. RDD Duplication & Column Un-Exclusion
- **Action**: Open [`proof/case-study-02-packslip-rdl-mod.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/proof/case-study-02-packslip-rdl-mod.md) Section 1.
- **Talk Track**:
  - *"In this synthetic lab scenario (`MFG01`), the receiving dock needs `ShipDtl.CustPartNum` on each line and the linked sales order Project Manager (`ShipDtl.OrderNum_ProjManager_c` `[S16]`) in the header."*
  - *"Per `[S15]`, we never edit the base `PackSlip` RDD. We duplicate it to `PackSlip_Custom` (*Default chosen for the lab, not confirmed against Epicor*) and clear the `Exclude` flag on `CustPartNum` and `OrderNum_ProjManager_c` (`[S12, S13, S14, S25]`). Because staging table columns are materialized when the report runs (`[S14]`, Approved Default 20), we stage a fresh `TableGuid` with `Archive Period = Day` (`[S21]`)."*

### `1:15 – 2:30` · 2. Copying the Report Style & Avoiding `Sync Dataset`
- **Action**: Walk through Steps 2 and 3 of `case-study-02-packslip-rdl-mod.md`.
- **Talk Track**:
  - *"Next, we copy the out-of-box `Standard - SSRS` style (`[S1, S5, S9]`) and point the copy to `PackSlip_Custom` (`[S15]`) and a custom `Report Location` under `reports/CustomReports/...` (`[S3, S5]`)."*
  - *"Crucially, we never click `Sync Dataset` on standard forms (`[S24, S25]`), which corrupts the multi-table dataset query. Instead, in Report Builder we append `T2.CustPartNum` and `T2.OrderNum_ProjManager_c` to the `SELECT` clause reading `ShipDtl_<GUID>` (`Parameters!TableGuid.Value` `[S13, S14, S19]`) and register both fields in Dataset Properties."*

### `2:30 – 4:00` · 3. Inspecting the Target Layout
- **Action**: Review the before/after comparison in Section 2 of Case Study 02.
- **Talk Track**:
  - *"The base layout lacks both fields [base render to be captured on the VM]. In the modified layout rendered against the staged GUID, Project Manager appears in the header block, and Customer Part Number renders next to PartNum in the line table [exact rendered values to be captured on the VM]."*

### `4:00 – 5:00` · 4. Mandatory Round-Trip Upload & Re-Download Check
- **Action**: Review Step 4 (`01-ssrs-forms.md` §7c).
- **Talk Track**:
  - *"Uploading a report is not the final step (`[S32, S2]`). Immediately after uploading to Report Style, we re-download the report into a clean verification folder (`[S32, S8]`) and confirm our query expression, field mappings, and table bindings are present in the downloaded file before marking the ticket complete."*
