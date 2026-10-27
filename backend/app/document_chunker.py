
from typing import Any

from app.document_parser import parse_all_documents


def chunk_document(
    document: dict[str, Any],
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict[str, Any]]:
    """
    Split one parsed document into overlapping text chunks.

    chunk_size: maximum number of characters per chunk.
    overlap: number of characters shared by consecutive chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    content = document["content"].strip()

    if not content:
        return []

    step = chunk_size - overlap
    chunks = []

    for start in range(0, len(content), step):
        end = start + chunk_size
        chunk_text = content[start:end].strip()

        if not chunk_text:
            continue

        chunk_number = len(chunks) + 1
        metadata = document["metadata"].copy()

        metadata["source"] = document["source"]
        metadata["source_path"] = document["source_path"]
        metadata["chunk_number"] = chunk_number

        document_id = metadata.get(
            "document_id",
            document["source"],
        )

        chunks.append(
            {
                "chunk_id": f"{document_id}_chunk_{chunk_number}",
                "text": chunk_text,
                "metadata": metadata,
            }
        )

        if end >= len(content):
            break

    return chunks


def chunk_all_documents(
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict[str, Any]]:
    """
    Parse all documents and split them into chunks.
    """
    documents = parse_all_documents()
    all_chunks = []

    for document in documents:
        document_chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        all_chunks.extend(document_chunks)

    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all_documents()

    print(f"Total chunks created: {len(chunks)}")

    for chunk in chunks:
        print("\n" + "=" * 60)
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['metadata']['source']}")
        print(f"Project ID: {chunk['metadata'].get('project_id', 'N/A')}")
        print(f"Invoice ID: {chunk['metadata'].get('invoice_id', 'N/A')}")
        print(f"Chunk number: {chunk['metadata']['chunk_number']}")
        print(f"Text: {chunk['text']}")
