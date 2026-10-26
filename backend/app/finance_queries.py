
from app.database import get_connection


def get_invoice_outstanding_balances():
    """Return outstanding balances for all invoices."""

    query = """
        SELECT
            invoice_id,
            invoice_amount,
            paid_amount,
            invoice_amount - paid_amount AS outstanding_balance,
            status
        FROM invoices
        ORDER BY invoice_id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    return [
        {
            "invoice_id": row[0],
            "invoice_amount": float(row[1]),
            "paid_amount": float(row[2]),
            "outstanding_balance": float(row[3]),
            "status": row[4],
        }
        for row in rows
    ]


def get_invoice_purchase_order_comparison():
    """Compare invoice amounts with their purchase-order totals."""

    query = """
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
        ORDER BY variance DESC, i.invoice_id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    return [
        {
            "invoice_id": row[0],
            "vendor_id": row[1],
            "po_id": row[2],
            "invoice_amount": float(row[3]),
            "po_total": float(row[4]),
            "variance": float(row[5]),
            "comparison_result": row[6],
        }
        for row in rows
    ]
