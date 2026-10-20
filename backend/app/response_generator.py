
import ollama


MODEL = "llama3.2:latest"


def generate_response(query: str, search_results: list):
    if not search_results:
        return (
            "The available IT documentation does not provide enough "
            "information to answer this question. Please contact IT "
            "support for assistance."
        )

    context = (
        f"Document: {search_results[0]['document']}\n"
        f"{search_results[0]['text']}"
    )

    prompt = f"""
You are an IT helpdesk assistant.

Answer the user's IT question using the provided documentation.

User question:
{query}

Relevant IT documentation:
{context}

Instructions:
- Answer only with information explicitly supported by the provided documentation.
- First determine whether the documentation actually addresses the user's question.
- A document being related to the question does not mean it contains the answer.
- Do not use general knowledge to fill gaps in the documentation.
- Do not invent or recommend steps, commands, websites, URLs, settings, or procedures.
- If the documentation does not directly support an answer, respond with exactly:
  "The available IT documentation does not provide enough information to answer this question. Please contact IT support for assistance."
- If the documentation supports only part of the answer, explain only the supported information and clearly state what is missing.
- Give step-by-step instructions only when the documentation explicitly provides those steps.
- Keep responses concise, clear, and appropriate for a non-technical employee.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    answer = response["message"]["content"].strip()
    answer_lower = answer.lower()

    insufficient_phrases = [
        "does not provide enough information",
        "does not provide a specific guide",
        "does not cover",
        "not able to find any information",
        "does not explicitly address",
        "not addressed in the provided documentation",
    ]

    if any(phrase in answer_lower for phrase in insufficient_phrases):
        return (
            "The available IT documentation does not provide enough "
            "information to answer this question. Please contact IT "
            "support for assistance."
        )

    return answer
