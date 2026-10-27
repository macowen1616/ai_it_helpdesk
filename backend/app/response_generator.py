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

    system_prompt = """
You are an IT helpdesk assistant. Your job is to explain the
provided IT documentation accurately.

STRICT RULES:
1. Treat the supplied documentation as your only source of facts.
2. Never add steps, websites, buttons, emails, commands, or procedures
   that are not explicitly stated in the documentation.
3. Do not fill gaps using your general IT knowledge.
4. Rephrase documented information if helpful, but do not change
   its meaning or add new factual details.
5. If the document describes a general process but not its exact
   steps, explain only the general process. Do not invent the steps.
6. If no useful answer is supported by the documentation, say:
   "The available IT documentation does not provide enough
   information to answer this question. Please contact IT support
   for assistance."

Example:
Documentation: "Use the organization's approved password-reset
process. Verify the user's identity before resetting the password."
Question: "How do I reset my password?"
Good answer: "Follow your organization's approved password-reset
process. Verify your identity according to the organization's
security procedures before the password is reset."
Bad answer: "Click Forgot Password on the login page and wait for
a reset email." Those steps were not documented.

Answer clearly and concisely. Do not add greetings or filler.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Question:\n{query}\n\n"
                    f"Documentation:\n{context}\n\n"
                    "Answer the question using only this documentation."
                ),
            },
        ],
        options={"temperature": 0},
    )

    answer = response["message"]["content"].strip()
    return answer if answer else fallback
