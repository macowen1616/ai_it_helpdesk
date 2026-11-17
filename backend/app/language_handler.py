
import ollama


MODEL = "llama3.2:latest"


def translate_query_to_english(query: str, language: str):
    """
    Translate a Spanish question into English for semantic search.
    English questions are returned unchanged.
    """

    if language == "en":
        return query

    if language != "es":
        raise ValueError("Unsupported language.")

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Translate the user's IT support question into English. "
                    "Preserve the original meaning and technical terms. "
                    "Return only the translated question. "
                    "Do not answer the question."
                ),
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        options={"temperature": 0},
    )

    return response["message"]["content"].strip()
