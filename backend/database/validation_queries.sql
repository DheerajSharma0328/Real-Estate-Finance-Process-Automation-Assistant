
-- ============================================================
-- Real Estate Finance Assistant
-- Day 2: Data Validation and Invoice Analysis Queries
-- ============================================================


-- Query 1: Compare invoice amounts with purchase-order totals.
-- Positive variance means the invoice is higher than the PO.

SELECT
    i.invoice_id,
    i.po_id,
    i.invoice_amount,
    po.po_total,
    i.invoice_amount - po.po_total AS variance
FROM invoices AS i
LEFT JOIN purchase_orders AS po
    ON i.po_id = po.po_id
ORDER BY i.invoice_id;


-- Query 2: Find invoices without a matching purchase order.
-- Expected result: zero rows.

SELECT
    i.invoice_id,
    i.po_id
FROM invoices AS i
LEFT JOIN purchase_orders AS po
    ON i.po_id = po.po_id
WHERE po.po_id IS NULL;


-- Query 3: Find invoices without a matching vendor.
-- Expected result: zero rows.

SELECT
    i.invoice_id,
    i.vendor_id
FROM invoices AS i
LEFT JOIN vendors AS v
    ON i.vendor_id = v.vendor_id
WHERE v.vendor_id IS NULL;


-- Query 4: Find payments without a matching invoice.
-- Expected result: zero rows.

SELECT
    p.payment_id,
    p.invoice_id
FROM payments AS p
LEFT JOIN invoices AS i
    ON p.invoice_id = i.invoice_id
WHERE i.invoice_id IS NULL;


-- Query 5: Find records referencing nonexistent properties.
-- Expected result: zero rows.

SELECT
    'purchase_orders' AS source_table,
    po.po_id AS record_id,
    po.property_id
FROM purchase_orders AS po
LEFT JOIN properties AS p
    ON po.property_id = p.property_id
WHERE p.property_id IS NULL

UNION ALL

SELECT
    'invoices',
    i.invoice_id,
    i.property_id
FROM invoices AS i
LEFT JOIN properties AS p
    ON i.property_id = p.property_id
WHERE p.property_id IS NULL

UNION ALL

SELECT
    'payments',
    pay.payment_id,
    pay.property_id
FROM payments AS pay
LEFT JOIN properties AS p
    ON pay.property_id = p.property_id
WHERE p.property_id IS NULL

UNION ALL

SELECT
    'budgets',
    b.budget_id,
    b.property_id
FROM budgets AS b
LEFT JOIN properties AS p
    ON b.property_id = p.property_id
WHERE p.property_id IS NULL;


-- Query 6: Find records referencing nonexistent cost codes.
-- Expected result: zero rows.

SELECT
    'purchase_orders' AS source_table,
    po.po_id AS record_id,
    po.cost_code
FROM purchase_orders AS po
LEFT JOIN cost_codes AS cc
    ON po.cost_code = cc.cost_code
WHERE cc.cost_code IS NULL

UNION ALL

SELECT
    'invoices',
    i.invoice_id,
    i.cost_code
FROM invoices AS i
LEFT JOIN cost_codes AS cc
    ON i.cost_code = cc.cost_code
WHERE cc.cost_code IS NULL

UNION ALL

SELECT
    'budgets',
    b.budget_id,
    b.cost_code
FROM budgets AS b
LEFT JOIN cost_codes AS cc
    ON b.cost_code = cc.cost_code
WHERE cc.cost_code IS NULL;


-- ============================================================
-- Query 7: Calculate outstanding balances for all invoices.
-- Outstanding balance = invoice amount - amount already paid.
-- ============================================================

SELECT
    invoice_id,
    invoice_amount,
    paid_amount,
    invoice_amount - paid_amount AS outstanding_balance,
    status
FROM invoices
ORDER BY invoice_id;


-- ============================================================
-- Query 8: Compare invoice amounts against purchase orders.
-- Positive variance means the invoice exceeds the PO amount.
-- ============================================================

SELECT
    i.invoice_id,
    i.vendor_id,
    i.po_id,
    i.invoice_amount,
    po.po_total,
    i.invoice_amount - po.po_total AS variance,
    CASE
        WHEN i.invoice_amount > po.po_total
            THEN 'Invoice exceeds PO'
        WHEN i.invoice_amount < po.po_total
            THEN 'Invoice below PO'
        ELSE 'Invoice matches PO'
    END AS comparison_result
FROM invoices AS i
JOIN purchase_orders AS po
    ON i.po_id = po.po_id
ORDER BY variance DESC;
