import ollama


MODEL = "llama3.2:latest"


def generate_response(query: str, search_results: list):
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
- Use only information explicitly stated in the provided documentation.
- Do not assume, infer, or fill in missing steps.
- Do not create website names, buttons, URLs, commands, settings, or procedures that are not explicitly mentioned in the documentation.
- If the documentation does not provide enough information to answer the question, say: "The available IT documentation does not provide enough information to answer this question. Please contact IT support for assistance."
- Give step-by-step instructions only when those steps are explicitly provided in the documentation.
- Keep the response concise and easy for a non-technical employee to understand.
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

    return response["message"]["content"]