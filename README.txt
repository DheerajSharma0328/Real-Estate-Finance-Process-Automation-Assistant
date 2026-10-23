REAL ESTATE FINANCE PROCESS AUTOMATION ASSISTANT — SYNTHETIC DATA PACK

Purpose
-------
Training dataset for Project 3. The dataset connects ERP-like structured finance records with
unstructured invoices, contracts, approval emails, draw packages, finance procedures and reconciliation notes.

Primary identifiers
-------------------
property_id, project_id, vendor_id, invoice_id, po_id, cost_code

Core relationships
------------------
Property -> Project -> Invoice -> Vendor
Invoice -> Purchase Order
Invoice -> Payment
Invoice -> Cost Code
Project/Property -> Budget
Invoice/PO/Project -> Documents

Important
---------
Students must not assume that an invoice is payable merely because it exists.
They should reconcile invoice amounts to POs, check budgets and supporting documents, and explain
why an item is approved, unpaid, partially paid, on hold or requires review.

All data is synthetic.
