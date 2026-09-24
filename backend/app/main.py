from fastapi import FastAPI
from .search import search_documents

app = FastAPI()


@app.get("/")
def root():
    return {"message": "IT Help Desk Assistant API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/search")
def search(query: str):
    return {
        "query": query,
        "results": search_documents(query)
    }