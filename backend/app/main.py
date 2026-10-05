from fastapi import FastAPI

from .semantic_search import semantic_search
from .response_generator import generate_response


app = FastAPI()


@app.get("/")
def root():
    return {"message": "IT Help Desk Assistant API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/search")
def search(query: str):
    results = semantic_search(query, top_k=1)

    response = generate_response(query, results)

    return {
        "query": query,
        "response": response,
        "source": results[0]["document"],
        "score": results[0]["score"],
    }

@app.get("/ask")
def ask(query: str):
    results = semantic_search(query, top_k=1)

    response = generate_response(query, results)

    return {
        "query": query,
        "response": response,
        "source": results[0]["document"],
        "score": results[0]["score"],
    }