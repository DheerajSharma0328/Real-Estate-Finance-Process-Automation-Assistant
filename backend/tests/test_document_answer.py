
from app.document_answer import generate_grounded_answer


def test_answer_uses_retrieved_evidence_and_source():
    results = [
        {
            "chunk_id": "DOC-DISPUTE-5004_chunk_1",
            "text": (
                "Invoice INV5004 is currently on hold. "
                "The invoice amount is INR 190,000 while PO7004 is "
                "INR 180,000. The variance is INR 10,000."
            ),
            "source": "INV5004_Dispute_Note.txt",
            "metadata": {
                "project_id": "PR204",
                "invoice_id": "INV5004",
            },
            "similarity_score": 0.764,
        }
    ]

    response = generate_grounded_answer(
        "Why is invoice INV5004 on hold?",
        results,
    )

    assert response["status"] == "success"
    assert "INR 10,000" in response["answer"]
    assert "INV5004_Dispute_Note.txt" in [
        source["source"] for source in response["sources"]
    ]
    assert response["sources"][0]["invoice_id"] == "INV5004"


def test_answer_returns_no_evidence_when_results_are_empty():
    response = generate_grounded_answer(
        "Why is invoice INV5004 on hold?",
        [],
    )

    assert response["status"] == "no_evidence"
    assert response["sources"] == []
    assert "could not find supporting evidence" in response["answer"]


def test_answer_rejects_empty_question():
    try:
        generate_grounded_answer("   ", [])
    except ValueError as error:
        assert str(error) == "Question cannot be empty."
    else:
        raise AssertionError("Expected ValueError for an empty question.")


def test_answer_rejects_irrelevant_results():
    results = [
        {
            "chunk_id": "unrelated_chunk_1",
            "text": "This document concerns a different topic.",
            "source": "unrelated.txt",
            "metadata": {"project_id": "PR204"},
            "similarity_score": 0.12,
        }
    ]

    response = generate_grounded_answer(
        "Why is invoice INV5004 on hold?",
        results,
    )

    assert response["status"] == "no_evidence"
    assert response["sources"] == []
