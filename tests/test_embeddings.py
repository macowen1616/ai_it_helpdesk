import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from backend.app.embeddings import create_embedding


text = "Wi-Fi connection problem"

embedding = create_embedding(text)

print("Embedding created successfully.")
print(f"Number of values: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")