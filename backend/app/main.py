import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from .semantic_search import semantic_search
from .response_generator import generate_response
from .language_handler import translate_query_to_english
from .database import get_connection

app = FastAPI()

password_hasher = PasswordHasher()

def require_login(request: Request):
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=401,
            detail="Please log in to access this resource."
        )

    return request.session["user_id"]

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(credentials: LoginRequest, request: Request):
    with get_connection() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (credentials.username.strip(),)
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password."
        )

    try:
        password_hasher.verify(
            user["password_hash"],
            credentials.password
        )
    except (VerifyMismatchError, VerificationError):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password."
        )

    request.session.clear()
    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]

    return {"message": "Login successful."}

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully."}

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SESSION_SECRET"],
    same_site="lax",
    https_only=False,
)

@app.get("/")
def root(request: Request):
    if "user_id" not in request.session:
        return FileResponse("frontend/login.html")

    return FileResponse("frontend/index.html")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/search")
def search(query: str, request: Request):
    require_login(request)
    results = semantic_search(query, top_k=1)

    return {
        "query": query,
        "results": results
    }


@app.get("/ask")
def ask(query: str, request: Request, language: str = "en"):
    require_login(request)
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
