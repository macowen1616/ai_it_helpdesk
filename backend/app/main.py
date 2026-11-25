import os
import time
from dotenv import load_dotenv
from httpx import request

load_dotenv()
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from .semantic_search import semantic_search
from .response_generator import generate_response
from .language_handler import translate_query_to_english
from .database import get_connection, initialize_database

app = FastAPI()

from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/login.html")
def login_page():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/index.html")
def dashboard_page():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.on_event("startup")
def startup_event():
    initialize_database()

password_hasher = PasswordHasher()

def require_login(request: Request):
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=401,
            detail="Please log in to access this resource."
        )

    return request.session["user_id"]

    def require_admin(request: Request):
        user_id = require_login(request)

    with get_connection() as connection:
        user = connection.execute(
            "SELECT role FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    if user is None or user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator access required."
        )

    return user_id

class LoginRequest(BaseModel):
    username: str
    password: str

class TicketRequest(BaseModel):
    subject: str
    description: str
    category: str = "General"
    priority: str = "Normal"

class TicketStatusRequest(BaseModel):
    status: str

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
    request.session["role"] = user["role"]

    return {
        "message": "Login successful.",
        "username": user["username"],
       "role": user["role"]
    }   

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully."}

@app.get("/me")
def get_current_user(request: Request):
    user_id = require_login(request)

    with get_connection() as connection:
        user = connection.execute(
            "SELECT username, role FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User account not found."
        )

    return {
        "username": user["username"],
        "role": user["role"]
    }

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SESSION_SECRET"],
    max_age=1800,
    same_site="lax",
    https_only=False,
)

@app.get("/ask")
def ask(query: str, request: Request, language: str = "en"):
    total_start = time.perf_counter()
    require_login(request)

    if language not in ("en", "es", "zh-TW"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Choose 'en', 'es', or 'zh-TW'."
        )

    # Measure translation time.
    translation_start = time.perf_counter()
    search_query = translate_query_to_english(query, language)
    translation_time = time.perf_counter() - translation_start

    # Measure semantic search time.
    search_start = time.perf_counter()
    results = semantic_search(search_query, top_k=1)
    search_time = time.perf_counter() - search_start

    # Measure AI response generation time.
    generation_start = time.perf_counter()
    response = generate_response(query, results, language)
    generation_time = time.perf_counter() - generation_start

    total_time = time.perf_counter() - total_start

    return {
        "query": query,
        "language": language,
        "response": response,
        "source": results[0]["document"] if results else None,
        "score": results[0]["score"] if results else None,
        "performance": {
            "translation_ms": round(translation_time * 1000, 2),
            "semantic_search_ms": round(search_time * 1000, 2),
            "response_generation_ms": round(generation_time * 1000, 2),
            "total_ms": round(total_time * 1000, 2),
        },
    }

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

@app.post("/tickets")
def create_ticket(ticket: TicketRequest, request: Request):
    require_login(request)

    allowed_priorities = ["Low", "Normal", "High", "Urgent"]
    allowed_categories = [
        "Network",
        "Hardware",
        "Software",
        "Account",
        "General"
    ]

    if ticket.priority not in allowed_priorities:
        raise HTTPException(
            status_code=400,
            detail="Invalid priority."
        )

    if ticket.category not in allowed_categories:
        raise HTTPException(
            status_code=400,
            detail="Invalid category."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                user_id,
                subject,
                description,
                category,
                priority
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.session["user_id"],
                ticket.subject,
                ticket.description,
                ticket.category,
                ticket.priority
            )
        )

        ticket_id = cursor.lastrowid

    return {
        "message": "Ticket submitted successfully.",
        "ticket_id": ticket_id
    }

@app.get("/tickets")
def get_tickets(request: Request):
    require_login(request)

    with get_connection() as connection:
        tickets = connection.execute(
            """
            SELECT
                id,
                subject,
                description,
                category,
                priority,
                status,
                created_at,
                updated_at
            FROM tickets
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (request.session["user_id"],)
        ).fetchall()

    return {
        "tickets": [dict(ticket) for ticket in tickets]
    }

@app.get("/admin/tickets")
def get_all_tickets(request: Request):
    require_admin(request)

    with get_connection() as connection:
        tickets = connection.execute("""
            SELECT
                tickets.id,
                tickets.subject,
                tickets.description,
                tickets.category,
                tickets.priority,
                tickets.status,
                tickets.created_at,
                tickets.updated_at,
                users.username
            FROM tickets
            JOIN users ON tickets.user_id = users.id
            ORDER BY tickets.created_at DESC
        """).fetchall()

    return {
        "tickets": [dict(ticket) for ticket in tickets]
    }

@app.patch("/admin/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    ticket_data: TicketStatusRequest,
    request: Request
):
    require_admin(request)

    allowed_statuses = [
        "Open",
        "In Progress",
        "Waiting on Employee",
        "Resolved",
        "Closed"
    ]

    if ticket_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket status."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tickets
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (ticket_data.status, ticket_id)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found."
            )

    return {
        "message": "Ticket status updated successfully.",
        "ticket_id": ticket_id,
        "status": ticket_data.status
    }