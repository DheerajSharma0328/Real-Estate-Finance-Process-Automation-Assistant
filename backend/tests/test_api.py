from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_endpoint():
    response = client.post(
        "/ask",
        json={"question": "What is invoice INV5001?"},
    )

    assert response.status_code == 200
    assert response.json()["question"] == "What is invoice INV5001?"
    assert response.json()["status"] == "success"
    assert response.json()["evidence"] == []


def test_empty_question_is_rejected():
    response = client.post("/ask", json={"question": ""})

    assert response.status_code == 422


def test_whitespace_question_is_rejected():
    response = client.post("/ask", json={"question": "   "})

    assert response.status_code == 422


def test_missing_question_is_rejected():
    response = client.post("/ask", json={})

    assert response.status_code == 422


def test_non_string_question_is_rejected():
    response = client.post("/ask", json={"question": 123})

    assert response.status_code == 422


def test_oversized_question_is_rejected():
    response = client.post("/ask", json={"question": "a" * 1001})

    assert response.status_code == 422


def test_invoice_comparison_endpoint():
    response = client.get("/invoices/INV5001/comparison")

    assert response.status_code == 200

    data = response.json()

    assert data["invoice_id"] == "INV5001"
    assert data["po_id"] == "PO7001"
    assert data["variance"] == 35000.0
    assert data["discrepancy_detected"] is True


def test_invoice_comparison_endpoint_unknown_invoice():
    response = client.get("/invoices/INV9999/comparison")

    assert response.status_code == 404



def test_invoice_outstanding_endpoint():
    response = client.get("/invoices/INV5002/outstanding")

    assert response.status_code == 200

    data = response.json()

    assert data["invoice_id"] == "INV5002"
    assert data["outstanding_balance"] == 150000.0


def test_invoice_outstanding_endpoint_unknown_invoice():
    response = client.get("/invoices/INV9999/outstanding")

    assert response.status_code == 404


def test_invoice_reconciliation_endpoint():
    response = client.get(
        "/invoices/INV5002/reconciliation"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["invoice_id"] == "INV5002"
    assert data["reconciled"] is True
    assert data["completed_payment_total"] == 125000.0


def test_invoice_reconciliation_endpoint_unknown_invoice():
    response = client.get(
        "/invoices/INV9999/reconciliation"
    )

    assert response.status_code == 404

def test_project_budget_endpoint():
    response = client.get("/projects/PR204/budget/CC101")

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == "PR204"
    assert data["cost_code"] == "CC101"
    assert data["budget_amount"] == 750000.0
    assert data["committed_variance"] == 70000.0
    assert data["over_budget"] is True


def test_project_budget_endpoint_unknown_record():
    response = client.get("/projects/PR9999/budget/CC999")

    assert response.status_code == 404



def test_postgres_invoice_outstanding_endpoint():
    sample_data = [
        {
            "invoice_id": "INV5002",
            "invoice_amount": 275000.0,
            "paid_amount": 125000.0,
            "outstanding_balance": 150000.0,
            "status": "Partially Paid",
        }
    ]

    with patch(
        "app.main.get_invoice_outstanding_balances",
        return_value=sample_data,
    ):
        response = client.get("/api/invoices/outstanding")

    assert response.status_code == 200
    assert response.json() == sample_data


def test_postgres_invoice_po_comparison_endpoint():
    sample_data = [
        {
            "invoice_id": "INV5001",
            "vendor_id": "V301",
            "po_id": "PO7001",
            "invoice_amount": 485000.0,
            "po_total": 450000.0,
            "variance": 35000.0,
            "comparison_result": "Invoice exceeds PO",
        }
    ]

    with patch(
        "app.main.get_invoice_purchase_order_comparison",
        return_value=sample_data,
    ):
        response = client.get("/api/invoices/po-comparison")

    assert response.status_code == 200
    assert response.json() == sample_data
