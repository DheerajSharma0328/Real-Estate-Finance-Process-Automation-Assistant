from app.inspect_invoices import (
    analyze_budget,
    calculate_outstanding_balance,
    compare_invoice_with_po,
    reconcile_invoice_payments,
)


def test_inv5001_comparison():
    comparison = compare_invoice_with_po("INV5001")

    assert comparison is not None
    assert comparison["invoice_id"] == "INV5001"
    assert comparison["po_id"] == "PO7001"
    assert comparison["invoice_amount"] == 485000.0
    assert comparison["po_amount"] == 450000.0
    assert comparison["variance"] == 35000.0
    assert comparison["result"] == (
        "Invoice is higher than the purchase order."
    )
    assert comparison["discrepancy_detected"] is True


def test_unknown_invoice_returns_none():
    comparison = compare_invoice_with_po("INV9999")

    assert comparison is None


def test_invoice_with_amount_difference_is_flagged():
    comparison = compare_invoice_with_po("INV5001")

    assert comparison is not None
    assert comparison["discrepancy_detected"] is True


def test_matching_invoice_amount_is_not_flagged():
    comparison = compare_invoice_with_po("INV5003")

    assert comparison is not None
    assert comparison["variance"] == 0.0
    assert comparison["discrepancy_detected"] is False



def test_inv5002_outstanding_balance():
    balance = calculate_outstanding_balance("INV5002")

    assert balance is not None
    assert balance["invoice_amount"] == 275000.0
    assert balance["paid_amount"] == 125000.0
    assert balance["outstanding_balance"] == 150000.0


def test_unknown_invoice_outstanding_balance_returns_none():
    balance = calculate_outstanding_balance("INV9999")

    assert balance is None


def test_pr204_cc101_is_over_budget():
    budget = analyze_budget("PR204", "CC101")

    assert budget is not None
    assert budget["budget_amount"] == 750000.0
    assert budget["committed_amount"] == 820000.0
    assert budget["committed_variance"] == 70000.0
    assert budget["over_budget"] is True


def test_pr204_cc202_is_within_budget():
    budget = analyze_budget("PR204", "CC202")

    assert budget is not None
    assert budget["committed_variance"] == -25000.0
    assert budget["over_budget"] is False


def test_unknown_project_cost_code_returns_none():
    budget = analyze_budget("PR204", "CC999")

    assert budget is None



def test_inv5002_payments_reconcile():
    result = reconcile_invoice_payments("INV5002")

    assert result is not None
    assert result["invoice_paid_amount"] == 125000.0
    assert result["completed_payment_total"] == 125000.0
    assert result["difference"] == 0.0
    assert result["payment_ids"] == ["PAY8001"]
    assert result["reconciled"] is True


def test_unknown_invoice_payment_reconciliation_returns_none():
    result = reconcile_invoice_payments("INV9999")

    assert result is None
