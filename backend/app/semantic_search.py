import json
import numpy as np
import ollama
from pathlib import Path


MODEL = "nomic-embed-text"

DOCUMENTS_DIR = Path(__file__).resolve().parents[2] / "documents"


def create_embedding(text: str):
    response = ollama.embed(
        model=MODEL,
        input=text
    )

    return np.array(response["embeddings"][0])


def cosine_similarity(vector_a, vector_b):
    dot_product = np.dot(vector_a, vector_b)

    magnitude_a = np.linalg.norm(vector_a)
    magnitude_b = np.linalg.norm(vector_b)

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def load_documents():
    documents = []

    for document_path in DOCUMENTS_DIR.glob("*.md"):
        text = document_path.read_text(encoding="utf-8")

        documents.append(
            {
                "document": document_path.name,
                "text": text,
            }
        )

    return documents

def load_embeddings():
    embeddings_path = (
        Path(__file__).resolve().parents[2]
        / "research"
        / "document_embeddings.json"
    )

    with open(embeddings_path, "r", encoding="utf-8") as file:
        return json.load(file)


def semantic_search(query: str, top_k: int = 3):
    query_embedding = create_embedding(query)

    documents = load_embeddings()
    results = []

    for document in documents:
        document_embedding = np.array(document["embedding"])

        score = cosine_similarity(
            query_embedding,
            document_embedding
        )

        results.append(
            {
                "document": document["document"],
                "score": float(score),
                "text": document["text"],
            }
        )

    results.sort(key=lambda result: result["score"], reverse=True)

    return results[:top_k]