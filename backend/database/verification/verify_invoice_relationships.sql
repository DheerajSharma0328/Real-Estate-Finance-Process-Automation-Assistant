
-- Day 5: Verify invoice relationships for INV5004.

SELECT
    i.invoice_id,
    i.property_id,
    i.project_id,
    i.vendor_id,
    i.po_id,
    p.property_name,
    v.vendor_name,
    po.po_total,
    i.invoice_amount,
    i.status
FROM invoices AS i
JOIN properties AS p
    ON p.property_id = i.property_id
JOIN vendors AS v
    ON v.vendor_id = i.vendor_id
JOIN purchase_orders AS po
    ON po.po_id = i.po_id
WHERE i.invoice_id = 'INV5004';

-- Verify that the purchase order has matching property and vendor IDs.

SELECT
    i.invoice_id,
    i.property_id,
    p.property_name,
    i.project_id,
    i.vendor_id,
    v.vendor_name,
    i.po_id,
    po.property_id AS po_property_id,
    po.vendor_id AS po_vendor_id,
    po.po_total,
    i.invoice_amount,
    i.status
FROM invoices AS i
JOIN properties AS p
    ON p.property_id = i.property_id
JOIN vendors AS v
    ON v.vendor_id = i.vendor_id
JOIN purchase_orders AS po
    ON po.po_id = i.po_id
WHERE i.invoice_id = 'INV5004';

