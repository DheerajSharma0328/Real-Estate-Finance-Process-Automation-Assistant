
from typing import Any

from sentence_transformers import SentenceTransformer, util

from app.document_chunker import chunk_all_documents


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def search_documents(
    query: str,
    top_k: int = 3,
    project_id: str | None = None,
    property_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Find document chunks that are semantically similar to a question.

    query: The user's question.
    top_k: Maximum number of results to return.
    project_id: Optional project filter, such as PR204.
    """

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    # 1. Load the document chunks.
    chunks = chunk_all_documents()

    # 2. Apply the project filter before searching.
    # 2. Apply business-identifier filters before semantic search.
    if project_id is not None:
        chunks = [
            chunk
            for chunk in chunks
            if chunk["metadata"].get("project_id") == project_id
    ]

    if property_id is not None:
        chunks = [
            chunk
            for chunk in chunks
            if chunk["metadata"].get("property_id") == property_id
    ]

    if not chunks:
        return []

    # 3. Load the embedding model on the CPU.
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    # 4. Generate an embedding for the user's question.
    query_embedding = model.encode(
        query,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    # 5. Generate embeddings for the document chunks.
    document_texts = [chunk["text"] for chunk in chunks]

    document_embeddings = model.encode(
        document_texts,
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    # 6. Calculate similarity between the question and each chunk.
    scores = util.cos_sim(
        query_embedding,
        document_embeddings,
    )[0]

    # 7. Rank results from most similar to least similar.
    result_count = min(top_k, len(chunks))
    top_results = scores.topk(result_count)

    results = []

    for index, score in zip(
        top_results.indices.tolist(),
        top_results.values.tolist(),
    ):
        chunk = chunks[index]

        results.append(
            {
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "source": chunk["metadata"]["source"],
                "metadata": chunk["metadata"],
                "similarity_score": round(float(score), 4),
            }
        )

    return results


if __name__ == "__main__":
    question = "Why is invoice INV5004 on hold?"

    results = search_documents(
        query=question,
        top_k=3,
        project_id="PR204",
    )

    print(f"\nQuestion: {question}")
    print(f"Results found: {len(results)}")

    for result in results:
        print("\n" + "=" * 60)
        print(f"Source: {result['source']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Similarity: {result['similarity_score']}")
        print(f"Project: {result['metadata'].get('project_id')}")
        print(f"Evidence:\n{result['text']}")
