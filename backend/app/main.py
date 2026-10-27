from app.document_search import search_documents
from typing import Literal
from app.document_answer import generate_grounded_answer
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.inspect_invoices import (
    analyze_budget,
    calculate_outstanding_balance,
    compare_invoice_with_po,
    reconcile_invoice_payments,
)

from app.finance_queries import (
    get_invoice_outstanding_balances,
    get_invoice_purchase_order_comparison,
)


app = FastAPI(
    title="Real Estate Finance Assistant",
    version="0.2.0",
)


# Allow the local React frontend to communicate with this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class AskResponse(BaseModel):
    question: str
    answer: str
    status: Literal["success", "unsupported"]
    evidence: list[dict[str, str]]
    trace: dict[str, str]

class DocumentSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    project_id: str | None = None
    top_k: int = Field(default=3, ge=1, le=10)

# ------------------------------------------------------------
# Health check
# ------------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "0.2.0",
    }


# ------------------------------------------------------------
# Existing invoice endpoints (Day 1)
# These continue to use the existing CSV-based functions.
# ------------------------------------------------------------

@app.get("/invoices/{invoice_id}/comparison")
def get_invoice_comparison(invoice_id: str):
    comparison = compare_invoice_with_po(invoice_id)

    if comparison is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice or linked purchase order was not found.",
        )

    return comparison


@app.get("/invoices/{invoice_id}/outstanding")
def get_invoice_outstanding_balance(invoice_id: str):
    balance = calculate_outstanding_balance(invoice_id)

    if balance is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice was not found.",
        )

    return balance


@app.get("/invoices/{invoice_id}/reconciliation")
def get_invoice_payment_reconciliation(invoice_id: str):
    reconciliation = reconcile_invoice_payments(invoice_id)

    if reconciliation is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice was not found.",
        )

    return reconciliation


@app.get("/projects/{project_id}/budget/{cost_code}")
def get_project_budget(project_id: str, cost_code: str):
    budget = analyze_budget(project_id, cost_code)

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget record was not found.",
        )

    return budget


# ------------------------------------------------------------
# New PostgreSQL endpoints (Day 2)
# These use the structured PostgreSQL database.
# ------------------------------------------------------------

@app.get("/api/invoices/outstanding")
def list_invoice_outstanding_balances():
    try:
        return get_invoice_outstanding_balances()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve invoice balances from the database.",
        )


@app.get("/api/invoices/po-comparison")
def list_invoice_purchase_order_comparisons():
    try:
        return get_invoice_purchase_order_comparison()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to compare invoices with purchase orders.",
        )


# ------------------------------------------------------------
# Existing question endpoint
# ------------------------------------------------------------

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot contain only whitespace.",
        )

    return AskResponse(
        question=question,
        answer=(
            "Your question was received. "
            "Finance-data processing will be added next."
        ),
        status="success",
        evidence=[],
        trace={
            "intent": "not_classified",
            "sources_used": "none",
            "validation": "passed",
        },
    )

# ------------------------------------------------------------
# Document search endpoint (Day 3)
# ------------------------------------------------------------


@app.post("/api/documents/search")
def document_search_endpoint(request: DocumentSearchRequest):
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=422,
            detail="Search query cannot contain only whitespace.",
        )

    try:
        results = search_documents(
            query=query,
            top_k=request.top_k,
            project_id=request.project_id,
        )

        answer_result = generate_grounded_answer(
            query=query,
            results=results,
        )

        return {
            "query": query,
            "answer": answer_result["answer"],
            "status": answer_result["status"],
            "sources": answer_result["sources"],
            "results": results,
            "result_count": len(results),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error
    except Exception as error:
        print(f"Document search failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to search documents.",
        ) from error
