
import ollama


MODEL = "llama3.2:latest"


def translate_query_to_english(query: str, language: str):
    """
    Translate Spanish or Traditional Chinese questions into English
    for semantic search. English questions are returned unchanged.
    """

    if language == "en":
        return query

    if language == "es":
        translator = (
            "You are a professional Spanish-to-English translator. "
            "Translate the user's entire question from Spanish into "
            "natural English. The output MUST be in English. "
            "Preserve the original meaning and technical terms. "
            "Return only the English translation. "
            "Do not answer the question."
        )

    elif language == "zh-TW":
        translator = (
            "You are a professional Traditional Chinese-to-English translator. "
            "Translate the user's entire question from Traditional Chinese "
            "into natural English. The output MUST be in English. "
            "Preserve the original meaning and technical terms. "
            "Return only the English translation. "
            "Do not answer the question."
        )

    else:
        raise ValueError("Unsupported language.")

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": translator,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        options={"temperature": 0},
    )

    translated = response["message"]["content"].strip()

    if not translated:
        raise ValueError("Translation returned an empty response.")

    return translated

