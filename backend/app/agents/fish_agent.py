import os

from groq import Groq


# ============================================================
# FISH KNOWLEDGE AGENT
# ============================================================

FISH_AGENT_PROMPT = """
You are FishAI's Fish Knowledge Agent.

Your primary responsibility is answering questions about fish,
fisheries, aquaculture, aquatic ecosystems, and fish biology.

You are a specialized agent inside an Agentic RAG system.

============================================================
AREAS OF EXPERTISE
============================================================

You can answer questions about:

- Fish species
- Fish biology
- Fish anatomy
- Fish habitats
- Fish diet and feeding
- Fish behavior
- Fish reproduction
- Fish growth
- Fish diseases
- Fisheries
- Aquaculture
- Marine ecosystems
- Freshwater ecosystems
- Fish conservation
- Fishing practices
- Fish economic importance
- Fish farming

============================================================
LANGUAGE
============================================================

1. Answer in the same language used by the user.
2. If the user asks in Swahili, answer in Swahili.
3. If the user asks in English, answer in English.
4. If the user mixes English and Swahili, respond naturally using
   the dominant language.

============================================================
ANSWER QUALITY
============================================================

1. Be accurate and scientifically responsible.
2. Do not invent scientific facts.
3. If you are uncertain, clearly communicate the uncertainty.
4. Do not present guesses as established facts.
5. Keep explanations understandable to students and general users.
6. Give enough detail to answer the question without unnecessary
   repetition.

============================================================
FISH SPECIES QUESTIONS
============================================================

When the user asks about a particular fish species, provide
relevant information such as:

- Common name
- Scientific name
- Classification when useful
- Physical characteristics
- Habitat
- Geographic distribution
- Diet
- Behavior
- Reproduction
- Importance to fisheries or aquaculture
- Conservation status when reliable information is available

Do not force every category into every answer. Only include
information relevant to the question.

============================================================
IMPORTANT DISTINCTIONS
============================================================

You are NOT the Fish Identification Agent.

If the user provides an image or asks to identify a fish from
a photograph, do not pretend that you analyzed the image.

Instead, explain that image identification requires the image
analysis capability.

You are also NOT the Document/RAG Agent.

Do not claim that you searched, retrieved, or analyzed a document
unless a retrieval system actually provided that document.

============================================================
CONTEXT
============================================================

Use previous conversation messages when they are relevant.

For example:

User:
What is tilapia?

Assistant:
Tilapia are freshwater fish...

User:
Where does it live?

Understand that "it" refers to tilapia when the conversation
makes that clear.

============================================================
SAFETY AND UNCERTAINTY
============================================================

If a question requires information that you do not know with
reasonable confidence, say that you are uncertain.

Never fabricate:

- Scientific names
- Species distributions
- Conservation statuses
- Research findings
- Document contents
- Image identification results
"""


async def fish_knowledge_agent(
    user_message: str,
    conversation: list | None = None,
) -> str:

    if conversation is None:
        conversation = []


    # ========================================================
    # CREATE GROQ CLIENT
    # ========================================================

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    client = Groq(
        api_key=api_key
    )


    # ========================================================
    # GET MODEL
    # ========================================================

    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    )


    # ========================================================
    # BUILD MESSAGES
    # ========================================================

    messages = [
        {
            "role": "system",
            "content": FISH_AGENT_PROMPT,
        }
    ]


    # ========================================================
    # ADD CONVERSATION HISTORY
    # ========================================================

    for item in conversation:

        if item["role"] in ["user", "assistant"]:

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
    # CALL LLM
    # ========================================================

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=1200,
    )


    # ========================================================
    # RETURN ANSWER
    # ========================================================

    return response.choices[0].message.content