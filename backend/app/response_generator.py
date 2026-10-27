

import ollama


MODEL = "llama3.2:latest"


def generate_response(query: str, search_results: list):
    fallback = (
        "The available IT documentation does not provide enough "
        "information to answer this question. Please contact IT "
        "support for assistance."
    )

    if not search_results:
        return fallback

    context = "\n\n".join(
        f"Document: {result['document']}\n{result['text']}"
        for result in search_results[:2]
    )

    prompt = f"""
You are a helpful IT helpdesk assistant for employees.

Answer the user's question using the relevant information in the
provided IT documentation.

User question:
{query}

IT documentation:
{context}

Rules:
- Read the documentation carefully and identify the information
  that answers the user's question.
- Explain the relevant information in plain, helpful language.
- If the documentation provides troubleshooting steps, present
  those steps as a numbered list.
- You may rephrase and organize the documented information to make
  it easier to understand.
- Do not invent commands, links, settings, procedures, or technical
  steps that are not supported by the documentation.
- If the documentation answers only part of the question, explain
  what it does answer and identify what information is missing.
- If the documentation contains no useful information for the
  question, say that the available IT documentation does not provide
  enough information and recommend contacting IT support.
- Do not refuse to answer just because the documentation does not
  contain every possible detail.
- Do not mention similarity scores or internal search processes.

Write a concise, useful answer for a non-technical employee.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options={"temperature": 0.1},
    )

    answer = response["message"]["content"].strip()

    return answer if answer else fallback

