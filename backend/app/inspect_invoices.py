
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FOLDER = PROJECT_ROOT / "data" / "structured_data"

INVOICES_FILE = DATA_FOLDER / "invoices.csv"
PURCHASE_ORDERS_FILE = DATA_FOLDER / "purchase_orders.csv"
BUDGETS_FILE = DATA_FOLDER / "budgets.csv"
PAYMENTS_FILE = DATA_FOLDER / "payments.csv"


def find_record(file_path, id_column, record_id):
    """Find a CSV record using a specified ID column."""
    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for record in reader:
            if record[id_column] == record_id:
                return record

    return None


def compare_invoice_with_po(invoice_id):
    """Compare an invoice amount with its purchase order total."""
    invoice = find_record(
        INVOICES_FILE,
        "invoice_id",
        invoice_id,
    )

    if invoice is None:
        return None

    purchase_order = find_record(
        PURCHASE_ORDERS_FILE,
        "po_id",
        invoice["po_id"],
    )

    if purchase_order is None:
        return None

    invoice_amount = float(invoice["invoice_amount"])
    po_amount = float(purchase_order["po_total"])
    variance = invoice_amount - po_amount

    if variance > 0:
        result = "Invoice is higher than the purchase order."
    elif variance < 0:
        result = "Invoice is lower than the purchase order."
    else:
        result = "Invoice matches the purchase order amount."

    discrepancy_detected = variance != 0

    return {
        "invoice_id": invoice["invoice_id"],
        "po_id": purchase_order["po_id"],
        "invoice_amount": invoice_amount,
        "po_amount": po_amount,
        "variance": variance,
        "result": result,
        "discrepancy_detected": discrepancy_detected,
    }



def calculate_outstanding_balance(invoice_id):
    """Calculate the unpaid balance for an invoice."""
    invoice = find_record(
        INVOICES_FILE,
        "invoice_id",
        invoice_id,
    )

    if invoice is None:
        return None

    invoice_amount = float(invoice["invoice_amount"])
    paid_amount = float(invoice["paid_amount"])
    outstanding_balance = invoice_amount - paid_amount

    return {
        "invoice_id": invoice["invoice_id"],
        "invoice_amount": invoice_amount,
        "paid_amount": paid_amount,
        "outstanding_balance": outstanding_balance,
        "status": invoice["status"],
    }



def analyze_budget(project_id, cost_code):
    """Analyze a budget record for a project and cost code."""

    # find_record returns only the first matching project record.
    # Search all records instead to identify the requested cost code.
    with BUDGETS_FILE.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        budget = None

        for record in reader:
            if (
                record["project_id"] == project_id
                and record["cost_code"] == cost_code
            ):
                budget = record
                break

    if budget is None:
        return None

    budget_amount = float(budget["budget_amount"])
    committed_amount = float(budget["committed_amount"])
    actual_amount = float(budget["actual_amount"])
    remaining_budget = float(budget["remaining_budget"])

    committed_variance = committed_amount - budget_amount

    return {
        "budget_id": budget["budget_id"],
        "project_id": budget["project_id"],
        "cost_code": budget["cost_code"],
        "budget_amount": budget_amount,
        "committed_amount": committed_amount,
        "actual_amount": actual_amount,
        "remaining_budget": remaining_budget,
        "committed_variance": committed_variance,
        "over_budget": committed_variance > 0,
    }



def reconcile_invoice_payments(invoice_id):
    """Compare completed payment records with the invoice's paid amount."""
    invoice = find_record(
        INVOICES_FILE,
        "invoice_id",
        invoice_id,
    )

    if invoice is None:
        return None

    recorded_paid_amount = float(invoice["paid_amount"])
    completed_payment_total = 0.0
    matching_payments = []

    with PAYMENTS_FILE.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for payment in reader:
            if payment["invoice_id"] != invoice_id:
                continue

            if payment["payment_status"].strip().lower() == "completed":
                completed_payment_total += float(payment["amount"])
                matching_payments.append(payment["payment_id"])

    difference = recorded_paid_amount - completed_payment_total

    return {
        "invoice_id": invoice_id,
        "invoice_paid_amount": recorded_paid_amount,
        "completed_payment_total": completed_payment_total,
        "difference": difference,
        "payment_ids": matching_payments,
        "reconciled": difference == 0,
    }


if __name__ == "__main__":
    invoice_id = input("Enter an invoice ID: ").strip()

    comparison = compare_invoice_with_po(invoice_id)

    if comparison is None:
        print("Invoice or purchase order was not found.")
    else:
        print("\nInvoice and purchase order comparison")
        print("--------------------------------------")

        for key, value in comparison.items():
            print(f"{key}: {value}")
