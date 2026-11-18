
import ollama


MODEL = "llama3.2:latest"


def generate_response(query: str, search_results: list, language: str = "en"):
    fallback = {
        "en": (
            "The available IT documentation does not provide enough "
            "information to answer this question. Please contact IT "
            "support for assistance."
        ),
        "es": (
            "La documentación de TI disponible no proporciona suficiente "
            "información para responder esta pregunta. Comuníquese con "
            "el soporte de TI para obtener ayuda."
        ),
        "zh-TW": (
            "目前可用的 IT 技術文件沒有提供足夠的資訊來回答這個問題。"
            "請聯絡 IT 技術支援人員以取得協助。"
        ),
    }

    if language not in ("en", "es", "zh-TW"):
        raise ValueError("Unsupported language.")

    if not search_results:
        return fallback[language]

    context = "\n\n".join(
        f"Document: {result['document']}\n{result['text']}"
        for result in search_results[:2]
    )

    response_language = {
        "en": "English",
        "es": "Spanish",
        "zh-TW": (
            "Traditional Chinese (繁體中文), using Taiwan terminology "
            "and Traditional Chinese characters. Do not use Simplified Chinese."
        ),
    }[language]

    system_prompt = f"""
You are an IT helpdesk assistant. Your job is to explain the
provided IT documentation accurately.

Respond in {response_language}.

STRICT RULES:
1. Treat the supplied documentation as your only source of facts.
2. Never add steps, websites, buttons, emails, commands, or procedures
   that are not explicitly stated in the documentation.
3. Do not fill gaps using your general IT knowledge.
4. Rephrase documented information if helpful, but do not change
   its meaning or add new factual details.
5. If the document describes a general process but not its exact
   steps, explain only the general process. Do not invent the steps.
6. If no useful answer is supported by the documentation, communicate
   that the available IT documentation does not provide enough
   information and advise the user to contact IT support.

Example:
Documentation: "Use the organization's approved password-reset
process. Verify the user's identity before resetting the password."
Question: "How do I reset my password?"
Good answer: "Follow your organization's approved password-reset
process. Verify your identity according to the organization's
security procedures before the password is reset."
Bad answer: "Click Forgot Password on the login page and wait for
a reset email." Those steps were not documented.

For Traditional Chinese:
- Always use Traditional Chinese characters.
- Use natural Taiwan terminology.
- Never respond using Simplified Chinese.

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
                    f"Answer the question in {response_language} "
                    "using only this documentation."
                ),
            },
        ],
        options={"temperature": 0},
    )

    answer = response["message"]["content"].strip()
    return answer if answer else fallback[language]
