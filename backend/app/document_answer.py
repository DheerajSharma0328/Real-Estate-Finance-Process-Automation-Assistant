
from typing import Any


# Results below this score are not considered strong enough
# to support an answer. This is a configurable starting point.
MIN_SIMILARITY_SCORE = 0.40


def generate_grounded_answer(
    query: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compose an answer from retrieved document evidence.

    The answer uses the retrieved text rather than inventing
    facts. Every source used in the answer is returned as a citation.
    """

    if not query.strip():
        raise ValueError("Question cannot be empty.")

    if not results:
        return {
            "answer": (
                "I could not find supporting evidence in the available "
                "documents, so I cannot answer this question reliably."
            ),
            "status": "no_evidence",
            "sources": [],
        }

    # Keep only results with a sufficient similarity score.
    relevant_results = [
        result
        for result in results
        if result.get("similarity_score", 0) >= MIN_SIMILARITY_SCORE
        and result.get("text", "").strip()
        and result.get("source", "").strip()
    ]

    if not relevant_results:
        return {
            "answer": (
                "The retrieved documents do not contain sufficiently "
                "relevant evidence to answer this question reliably."
            ),
            "status": "no_evidence",
            "sources": [],
        }

    # Use the strongest matching evidence first.
    relevant_results.sort(
        key=lambda result: result["similarity_score"],
        reverse=True,
    )

    # Keep up to two sources to avoid overwhelming the answer.
    selected_results = relevant_results[:2]

    evidence_statements = [
        result["text"].strip()
        for result in selected_results
    ]

    answer = (
        "Based on the retrieved document evidence: "
        + " ".join(evidence_statements)
    )

    sources = [
        {
            "source": result["source"],
            "chunk_id": result["chunk_id"],
            "similarity_score": result["similarity_score"],
            "project_id": result["metadata"].get("project_id"),
            "invoice_id": result["metadata"].get("invoice_id"),
        }
        for result in selected_results
    ]

    return {
        "answer": answer,
        "status": "success",
        "sources": sources,
    }
