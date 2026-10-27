
from app.document_search import search_documents


def test_search_finds_relevant_invoice_evidence():
    results = search_documents(
        query="Why is invoice INV5004 on hold?",
        top_k=3,
        project_id="PR204",
    )

    assert len(results) > 0
    assert results[0]["source"] == "INV5004_Dispute_Note.txt"
    assert "INR 10,000" in results[0]["text"]
    assert results[0]["metadata"]["project_id"] == "PR204"


def test_search_returns_empty_for_unknown_project():
    results = search_documents(
        query="What does the invoice say?",
        project_id="PR999",
    )

    assert results == []


def test_search_rejects_empty_query():
    try:
        search_documents(query="   ")
    except ValueError as error:
        assert str(error) == "Search query cannot be empty."
    else:
        raise AssertionError("Expected ValueError for an empty query.")


def test_search_rejects_invalid_top_k():
    try:
        search_documents(
            query="Why is invoice INV5004 on hold?",
            top_k=0,
        )
    except ValueError as error:
        assert str(error) == "top_k must be greater than 0."
    else:
        raise AssertionError("Expected ValueError for top_k=0.")
