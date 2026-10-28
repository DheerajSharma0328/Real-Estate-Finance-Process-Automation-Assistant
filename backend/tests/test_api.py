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


def test_document_search_unknown_project_returns_no_evidence():
    with patch("app.main.search_documents", return_value=[]):
        response = client.post(
            "/api/documents/search",
            json={
                "query": "Why is this invoice on hold?",
                "project_id": "PR999",
                "top_k": 3,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "no_evidence"
    assert data["result_count"] == 0
    assert data["results"] == []
    assert data["sources"] == []
    assert "could not find supporting evidence" in data["answer"].lower()


def test_property_evidence_endpoint_success():
    property_record = {
        "property_id": "P204",
        "property_name": "Cedar Heights",
        "city": "Delhi",
        "property_type": "Residential Tower",
        "project_id": "PR204",
        "status": "Active",
    }

    invoice = {
        "invoice_id": "INV5004",
        "property_id": "P204",
        "project_id": "PR204",
        "po_id": "PO7004",
        "invoice_amount": 190000.0,
        "paid_amount": 0.0,
        "status": "On Hold",
        "po_total": 180000.0,
        "variance": 10000.0,
    }

    search_results = [
        {
            "chunk_id": "DOC-DISPUTE-5004_chunk_1",
            "text": (
                "Invoice INV5004 is on hold. The invoice amount is "
                "INR 190,000 while PO7004 is INR 180,000. "
                "A revised invoice or written approval is required."
            ),
            "source": "INV5004_Dispute_Note.txt",
            "metadata": {
                "property_id": "P204",
                "project_id": "PR204",
                "invoice_id": "INV5004",
            },
            "similarity_score": 0.764,
        }
    ]

    with (
        patch(
            "app.main.get_property_finance_record",
            return_value={
                "property": property_record,
                "invoices": [invoice],
            },
        ),
        patch(
            "app.main.search_documents",
            return_value=search_results,
        ),
    ):
        response = client.post(
            "/api/properties/P204/evidence",
            json={
                "query": "Why is invoice INV5004 on hold?",
                "invoice_id": "INV5004",
                "top_k": 3,
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["property"]["property_id"] == "P204"
    assert len(data["invoices"]) == 1
    assert data["invoices"][0]["invoice_id"] == "INV5004"
    assert data["invoices"][0]["variance"] == 10000.0
    assert data["sources"][0]["source"] == "INV5004_Dispute_Note.txt"
    assert data["sources"][0]["property_id"] == "P204"


def test_property_evidence_unknown_property():
    with patch(
        "app.main.get_property_finance_record",
        return_value=None,
    ):
        response = client.post(
            "/api/properties/P999/evidence",
            json={"query": "Find supporting evidence"},
        )

    assert response.status_code == 404
    assert "Property P999 was not found" in response.json()["detail"]


def test_property_evidence_rejects_invoice_from_another_property():
    with patch(
        "app.main.get_property_finance_record",
        return_value={
            "property": {
                "property_id": "P205",
                "property_name": "Riverside Plaza",
                "city": "Gurugram",
                "property_type": "Commercial",
                "project_id": "PR205",
                "status": "Active",
            },
            "invoices": [],
        },
    ):
        response = client.post(
            "/api/properties/P205/evidence",
            json={
                "query": "Why is invoice INV5001 on hold?",
                "invoice_id": "INV5001",
            },
        )

    assert response.status_code == 404
    assert "INV5001" in response.json()["detail"]
    assert "P205" in response.json()["detail"]


def test_property_evidence_rejects_document_with_mismatched_property():
    with (
        patch(
            "app.main.get_property_finance_record",
            return_value={
                "property": {
                    "property_id": "P204",
                    "property_name": "Cedar Heights",
                    "city": "Delhi",
                    "property_type": "Residential Tower",
                    "project_id": "PR204",
                    "status": "Active",
                },
                "invoices": [],
            },
        ),
        patch(
            "app.main.search_documents",
            return_value=[
                {
                    "chunk_id": "wrong_chunk",
                    "text": "Unrelated property evidence.",
                    "source": "UNRELATED_INVOICE_P206.txt",
                    "metadata": {
                        "property_id": "P206",
                        "project_id": "PR206",
                        "invoice_id": "INV9999",
                    },
                    "similarity_score": 0.9,
                }
            ],
        ),
    ):
        response = client.post(
            "/api/properties/P204/evidence",
            json={"query": "Find evidence", "top_k": 3},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["result_count"] == 0
    assert data["results"] == []
    assert data["sources"] == []
    assert data["status"] == "no_evidence"
