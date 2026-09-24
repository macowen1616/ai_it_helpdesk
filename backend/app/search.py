from pathlib import Path


DOCUMENTS_DIR = Path(__file__).resolve().parents[2] / "documents"

STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "am",
    "my",
    "to",
    "of",
    "in",
    "on",
    "for",
    "and",
    "or",
    "but",
    "can",
    "cannot",
    "could",
    "would",
    "should",
    "i",
    "me",
    "it",
}


def search_documents(query: str):
    query_words = {
        word.strip(".,!?():;\"'").lower()
        for word in query.split()
    }

    query_words -= STOP_WORDS

    results = []

    for document_path in DOCUMENTS_DIR.glob("*.md"):
        text = document_path.read_text(encoding="utf-8")

        text_words = {
            word.strip(".,!?():;\"'").lower()
            for word in text.split()
        }

        matches = query_words.intersection(text_words)
        score = len(matches)

        if score > 0:
            results.append(
                {
                    "document": document_path.name,
                    "score": score,
                    "matches": list(matches),
                }
            )

    results.sort(key=lambda result: result["score"], reverse=True)

    return results