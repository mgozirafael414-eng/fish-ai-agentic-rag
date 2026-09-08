import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not configured. "
        "Please add it to your .env file."
    )


client = Groq(
    api_key=GROQ_API_KEY
)


SYSTEM_PROMPT = """
You are FishAI, an intelligent AI assistant.

Your main specialization is:
- Fish species identification
- Fish biology
- Fisheries
- Aquaculture
- Fish habitats
- Marine and freshwater ecosystems

However, you are also a general-purpose AI assistant.
You should answer general questions about science, technology,
programming, education, mathematics, and everyday topics.

Important rules:
1. Answer in the same language used by the user.
2. Be clear, accurate, and helpful.
3. Do not invent facts.
4. If you are uncertain, say so.
5. For fish-related questions, provide useful scientific details.
6. Do not claim that an image was analyzed unless an image was actually provided.
7. Do not claim that documents were retrieved unless the RAG system actually retrieved them.
"""


async def generate_ai_response(
    user_message: str,
    conversation: list | None = None,
) -> str:

    if conversation is None:
        conversation = []

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    for item in conversation:
        if item["role"] in ["user", "assistant"]:
            messages.append(
                {
                    "role": item["role"],
                    "content": item["content"],
                }
            )

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
    )

    return response.choices[0].message.content