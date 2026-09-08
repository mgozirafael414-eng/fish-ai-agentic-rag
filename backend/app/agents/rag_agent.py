import os

from dotenv import load_dotenv
from groq import Groq

from app.rag.retriever import retrieve_relevant_chunks


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# RAG AGENT SYSTEM PROMPT
# ============================================================

RAG_AGENT_PROMPT = """
You are FishAI's RAG Retrieval Agent.

Your responsibility is to answer questions using information
retrieved from the user's knowledge base.

IMPORTANT RULES:

1. Use the retrieved context as the primary source of information.
2. Do not invent information that is not supported by the context.
3. If the context does not contain enough information to answer
   the question, clearly say that the available documents do not
   contain enough information.
4. Do not pretend that you searched documents if no context
   was retrieved.
5. Answer in the same language used by the user.
6. If the user asks in Swahili, answer in Swahili.
7. If the user asks in English, answer in English.
8. Be clear and easy to understand.
9. Use the source information provided with the retrieved context.
10. Do not confuse retrieved document information with general
    knowledge.
11. Do not mention information that is not supported by the
    retrieved context.

The retrieved context is provided below.

================ RETRIEVED CONTEXT ================

{context}

====================================================
"""


# ============================================================
# BUILD RAG CONTEXT
# ============================================================

def build_context(
    retrieved_chunks: list[dict]
) -> str:

    if not retrieved_chunks:
        return (
            "No relevant information was retrieved "
            "from the knowledge base."
        )


    context_parts = []


    for index, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        content = chunk.get(
            "content",
            ""
        )


        metadata = chunk.get(
            "metadata",
            {}
        )


        source = metadata.get(
            "source",
            "Unknown source"
        )


        chunk_index = metadata.get(
            "chunk_index",
            "Unknown"
        )


        context_parts.append(
            f"""
[Retrieved Source {index}]

Document: {source}
Chunk: {chunk_index}

Content:
{content}
"""
        )


    return "\n".join(
        context_parts
    )


# ============================================================
# BUILD SOURCE LIST
# ============================================================

def build_sources(
    retrieved_chunks: list[dict]
) -> list[str]:

    sources = []


    for chunk in retrieved_chunks:

        metadata = chunk.get(
            "metadata",
            {}
        )


        source = metadata.get(
            "source"
        )


        chunk_index = metadata.get(
            "chunk_index"
        )


        if not source:
            continue


        if chunk_index is not None:

            source_text = (
                f"{source} — "
                f"Chunk {chunk_index}"
            )

        else:

            source_text = source


        if source_text not in sources:

            sources.append(
                source_text
            )


    return sources


# ============================================================
# RAG AGENT
# ============================================================

async def rag_agent(
    user_message: str,
    conversation: list | None = None,
    n_results: int = 3,
) -> str:

    if conversation is None:
        conversation = []


    # ========================================================
    # CHECK API KEY
    # ========================================================

    api_key = os.getenv(
        "GROQ_API_KEY"
    )


    if not api_key:

        raise ValueError(
            "GROQ_API_KEY is not configured."
        )


    # ========================================================
    # RETRIEVE RELEVANT CHUNKS
    # ========================================================

    retrieved_chunks = (
        retrieve_relevant_chunks(
            query=user_message,
            n_results=n_results,
        )
    )


    print(
        f"[RAG] Retrieved chunks: "
        f"{len(retrieved_chunks)}"
    )


    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    context = build_context(
        retrieved_chunks
    )


    # ========================================================
    # CREATE GROQ CLIENT
    # ========================================================

    client = Groq(
        api_key=api_key
    )


    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    )


    # ========================================================
    # CREATE SYSTEM PROMPT
    # ========================================================

    system_prompt = RAG_AGENT_PROMPT.format(
        context=context
    )


    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]


    # ========================================================
    # ADD CONVERSATION HISTORY
    # ========================================================

    for item in conversation:

        if item["role"] in [
            "user",
            "assistant"
        ]:

            messages.append(
                {
                    "role": item["role"],
                    "content": item["content"],
                }
            )


    # ========================================================
    # ADD CURRENT USER QUESTION
    # ========================================================

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=1200,
    )


    answer = (
        response
        .choices[0]
        .message
        .content
    )


    # ========================================================
    # ADD SOURCE INFORMATION
    # ========================================================

    sources = build_sources(
        retrieved_chunks
    )


    if sources:

        answer += (
            "\n\n📚 **Sources**\n\n"
        )


        for index, source in enumerate(
            sources,
            start=1
        ):

            answer += (
                f"{index}. {source}\n"
            )


    return answer