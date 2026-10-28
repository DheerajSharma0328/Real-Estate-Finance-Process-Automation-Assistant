
from typing import Any

from app.database import get_connection


def get_property_finance_record(property_id: str) -> dict[str, Any] | None:
    """
    Retrieve a property and its invoice/PO facts from PostgreSQL.

    Return None if the property does not exist.
    """
    property_query = """
        SELECT property_id, property_name, city, property_type,
               project_id, status
        FROM properties
        WHERE property_id = %s;
    """

    invoice_query = """
        SELECT
            i.invoice_id,
            i.property_id,
            i.project_id,
            i.po_id,
            i.invoice_amount,
            i.paid_amount,
            i.status,
            po.po_total,
            i.invoice_amount - po.po_total AS variance
        FROM invoices AS i
        LEFT JOIN purchase_orders AS po ON po.po_id = i.po_id
        WHERE i.property_id = %s
        ORDER BY i.invoice_id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(property_query, (property_id,))
            row = cursor.fetchone()

            if row is None:
                return None

            property_record = {
                "property_id": row[0],
                "property_name": row[1],
                "city": row[2],
                "property_type": row[3],
                "project_id": row[4],
                "status": row[5],
            }

            cursor.execute(invoice_query, (property_id,))
            invoice_rows = cursor.fetchall()

    invoices = []

    for row in invoice_rows:
        invoice_property_id = row[1]
        invoice_project_id = row[2]

        # Do not include an invoice whose identifiers disagree
        # with the selected property's identifiers.
        if (
            invoice_property_id != property_record["property_id"]
            or invoice_project_id != property_record["project_id"]
        ):
            continue

        invoices.append(
            {
                "invoice_id": row[0],
                "property_id": invoice_property_id,
                "project_id": invoice_project_id,
                "po_id": row[3],
                "invoice_amount": float(row[4]),
                "paid_amount": float(row[5]),
                "status": row[6],
                "po_total": float(row[7]) if row[7] is not None else None,
                "variance": float(row[8]) if row[8] is not None else None,
            }
        )

    return {
        "property": property_record,
        "invoices": invoices,
    }
