import json
from pathlib import Path

from backend.app.semantic_search import create_embedding, load_documents


OUTPUT_FILE = Path(__file__).resolve().parents[1] / "research" / "document_embeddings.json"


documents = load_documents()

embedded_documents = []

for document in documents:
    print(f"Creating embedding for {document['document']}...")

    embedding = create_embedding(document["text"])

    embedded_documents.append(
        {
            "document": document["document"],
            "text": document["text"],
            "embedding": embedding.tolist(),
        }
    )

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(embedded_documents, file)

print(f"\nSaved {len(embedded_documents)} document embeddings to:")
print(OUTPUT_FILE)