# Case Study 02: Packing Slip (`PackSlip`) RDD + RDL Modification (One-Page Summary)

> **Notice**: Lab exercise on synthetic data. Not client work.
>
> **Synthetic Lab Disclosure & Environment Notice**: All parameters shown (`MFG01 Manufacturing Corp`, `CUST01`, `PackNum = 50001`, `CP-8842-A`, `Sarah Connor`) represent synthetic training definitions from [`labs/report/R1-packslip-add-custpartnum.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/labs/report/R1-packslip-add-custpartnum.md) and [`labs/report/R2-packslip-linked-table-ud.md`](file:///Users/alhasibtamim/Projects/kinetic-subcontract-lab/labs/report/R2-packslip-linked-table-ud.md). No SQL Server or SSRS ran on this authoring host. No Epicor screenshots, logos, or raw RDL XML text are included.
> **Lab Banner**: *"Default chosen for the lab, not confirmed against Epicor."* applies to custom RDD/style names (`PackSlip_Custom`), `Report Location` path `reports/CustomReports/PackingSlip/PackSlip_Custom`, Report Builder dialog labels (`fx`, `Add > Query Field`), and the lab SQL stand-in procedures.

---

## 1. Requirement & Safe Customization Workflow
Receiving at synthetic account `CUST01` (*Acme Industrial Technologies*) needs **Customer Part Number** (`ShipDtl.CustPartNum`) on the Packing Slip line table and **Order Project Manager** (`ShipDtl.OrderNum_ProjManager_c` linked from `OrderHed` `[S16]`) in the Packing Slip header for synthetic pack `PackNum = 50001`:
1. **Duplicate the RDD (`[S15]`) & Un-exclude Columns (`[S12, S13, S14, S25]`)**: Both `CustPartNum` and `OrderNum_ProjManager_c` are excluded (`Exclude = 1`) in the base `PackSlip` RDD and must be un-excluded before staging a new `TableGuid` (`a1111111111111111111111111111101`, Approved Default 20).
2. **Copy the System Report Style (`[S1, S5, S9]`)**: Point the copied style to `PackSlip_Custom` (`[S15]`) and custom `Report Location` (`[S3, S5]`), never editing the system style (`[S1, S9]`).
3. **Edit Dataset Query & Fields Manually — Never Click `Sync Dataset` (`[S24, S25]`)**: Add `T2.CustPartNum`, `T2.OrderNum_ProjManager_c`, `T5.LblCustPartNum`, and `T5.LblProjManager` to the `Parameters!TableGuid.Value` SQL query (`[S13, S14, S19, S8]`) and register them in the Dataset Fields list.
4. **Round-Trip Upload & Re-Download (`[S32, S8]`, `01-ssrs-forms.md` §7c)**: Upload via Report Style and immediately re-download to verify the changes persisted.

---

## 2. Report Builder Render Preview (Before vs. After)

> **TODO**: PackSlip PDF render: to be produced on the VM.
> Specific rendered values, layout metrics, and execution timings below are marked `[to be captured on the VM]` because no SSRS instance ran in this authoring session.

### Before Modification (Base Standard Layout — Fictional Pack `50001`)
```text
================================================================================
[Header block to be captured on the VM]
MFG01 Manufacturing Corp                                            PACKING SLIP
--------------------------------------------------------------------------------
Pack Number: [to be captured on the VM]  Ship Date:   [to be captured on the VM]
Customer:    [to be captured on the VM]  Tracking #:  [to be captured on the VM]
Ship To:     [to be captured on the VM]
--------------------------------------------------------------------------------
Line | Order / Ln / Rel | Part Number | Description                      |   Qty
-----+------------------+-------------+----------------------------------+------
   1 | [to be captured] | [captured]  | [to be captured on the VM]       | [qty]
================================================================================
```

### After Modification (Un-Excluded `CustPartNum` & Linked `OrderNum_ProjManager_c`)
```text
================================================================================
[Header block to be captured on the VM]
MFG01 Manufacturing Corp                                            PACKING SLIP
--------------------------------------------------------------------------------
Pack Number: [to be captured on the VM]  Ship Date:        [captured on the VM]
Customer:    [to be captured on the VM]  Tracking #:       [captured on the VM]
Ship To:     [to be captured on the VM]  Project Manager:  [to be captured on the VM]
--------------------------------------------------------------------------------
Line | Order/Ln/Rel | Part Number | Cust Part # | Description              | Qty
-----+--------------+-------------+-------------+--------------------------+----
   1 | [to be captured on the VM] | [captured]  | [to be captured on VM]   | [ ]
================================================================================
```
