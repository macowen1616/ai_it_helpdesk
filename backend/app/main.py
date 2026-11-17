
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .semantic_search import semantic_search
from .response_generator import generate_response
from .language_handler import translate_query_to_english


app = FastAPI()


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/search")
def search(query: str):
    results = semantic_search(query, top_k=1)

    return {
        "query": query,
        "results": results
    }


@app.get("/ask")
def ask(query: str, language: str = "en"):
    if language not in ("en", "es"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Choose 'en' or 'es'."
        )

    # Translate Spanish questions into English for document retrieval.
    search_query = translate_query_to_english(query, language)

    # Search the existing English IT documentation.
    results = semantic_search(search_query, top_k=1)

    # Generate the response in the user's selected language.
    response = generate_response(query, results, language)

    return {
        "query": query,
        "language": language,
        "response": response,
        "source": results[0]["document"] if results else None,
        "score": results[0]["score"] if results else None,
    }
