
from typing import Any

from sentence_transformers import SentenceTransformer

from app.document_chunker import chunk_all_documents


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def generate_embeddings(
    chunks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Generate an embedding vector for each text chunk.

    Returns copies of the chunks with an additional 'embedding' field.
    """
    if not chunks:
        return []

    model = SentenceTransformer(MODEL_NAME, device="cpu")

    texts = [chunk["text"] for chunk in chunks]

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    embedded_chunks = []

    for chunk, vector in zip(chunks, vectors):
        embedded_chunk = chunk.copy()
        embedded_chunk["embedding"] = vector.tolist()
        embedded_chunks.append(embedded_chunk)

    return embedded_chunks


def embed_all_documents() -> list[dict[str, Any]]:
    """
    Chunk all documents and generate embeddings for their text.
    """
    chunks = chunk_all_documents()
    return generate_embeddings(chunks)


if __name__ == "__main__":
    embedded_chunks = embed_all_documents()

    print(f"\nTotal embedded chunks: {len(embedded_chunks)}")

    if embedded_chunks:
        first_chunk = embedded_chunks[0]

        print(f"First chunk ID: {first_chunk['chunk_id']}")
        print(f"Source: {first_chunk['metadata']['source']}")
        print(f"Embedding dimensions: {len(first_chunk['embedding'])}")
        print(f"First 5 numbers: {first_chunk['embedding'][:5]}")
