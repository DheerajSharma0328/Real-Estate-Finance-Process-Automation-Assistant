
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "documents" / "unstructured_documents"


def parse_document(file_path: Path) -> dict[str, Any]:
    """
    Read a text document and separate its metadata from its body.
    The first blank line separates the header from the body.
    """
    text = file_path.read_text(encoding="utf-8").strip()

    lines = text.splitlines()

    # Find the first blank line separating metadata and body.
    separator_index = next(
        (
            index
            for index, line in enumerate(lines)
            if not line.strip()
        ),
        len(lines),
    )

    header_lines = lines[:separator_index]
    content_lines = lines[separator_index + 1:]

    # Extract metadata only from the header.
    metadata: dict[str, str] = {}

    for line in header_lines:
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        metadata_key = key.strip().lower().replace(" ", "_")
        metadata[metadata_key] = value.strip()

    # Preserve all body text, including colons and blank lines.
    content = "\n".join(content_lines).strip()

    return {
        "source": file_path.name,
        "source_path": str(file_path.relative_to(PROJECT_ROOT)),
        "metadata": metadata,
        "content": content,
    }


def parse_all_documents() -> list[dict[str, Any]]:
    """
    Parse all .txt documents in the unstructured documents folder.
    """
    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(
            f"Document directory not found: {DOCUMENTS_DIR}"
        )

    file_paths = sorted(DOCUMENTS_DIR.glob("*.txt"))

    if not file_paths:
        raise FileNotFoundError(
            f"No .txt documents found in: {DOCUMENTS_DIR}"
        )

    return [
        parse_document(file_path)
        for file_path in file_paths
    ]


if __name__ == "__main__":
    documents = parse_all_documents()

    print(f"Parsed {len(documents)} documents.")

    for document in documents:
        print(f"\nSource: {document['source']}")
        print(f"Metadata: {document['metadata']}")
        print(f"Content preview: {document['content'][:150]}")
