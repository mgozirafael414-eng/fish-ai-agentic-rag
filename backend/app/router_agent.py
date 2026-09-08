# backend/app/router_agent.py

import re


# ============================================================
# QUERY ROUTER AGENT
# ============================================================

def route_query(user_message: str) -> str:
    """
    Decide which agent should handle the user's query.
    """

    message = user_message.lower().strip()

    # --------------------------------------------------------
    # 1. IMAGE / FISH IDENTIFICATION
    # --------------------------------------------------------

    image_keywords = [
        "image",
        "photo",
        "picture",
        "picha",
        "identify this fish",
        "identify fish",
        "what fish is this",
        "what species is this",
        "species of this fish",
        "tambua samaki",
        "aina gani ya samaki",
    ]

    if any(keyword in message for keyword in image_keywords):
        return "FISH_IDENTIFICATION"


    # --------------------------------------------------------
    # 2. DOCUMENT QUERY
    # --------------------------------------------------------

    document_keywords = [
        "document",
        "pdf",
        "file",
        "report",
        "paper",
        "research paper",
        "according to the document",
        "according to this document",
        "kwenye document",
        "kwenye pdf",
        "kwenye faili",
        "tafiti",
    ]

    if any(keyword in message for keyword in document_keywords):
        return "DOCUMENT_QUERY"


    # --------------------------------------------------------
    # 3. TIME QUERY
    # --------------------------------------------------------

    time_keywords = [
        # English
        "what time is it",
        "what's the time",
        "current time",
        "current date",
        "what is the current time",
        "what is the time now",
        "time now",
        "time right now",
        "tell me the time",
        "show me the time",
        "exact time",
        "local time",
        "today's date",
        "what day is it",

        # Swahili
        "saa ngapi",
        "saa ngapi sasa",
        "ni saa ngapi",
        "ni saa ngapi sasa",
        "muda wa sasa",
        "muda gani sasa",
        "wakati gani sasa",
        "saa ya sasa",
        "tarehe ya leo",
        "leo ni tarehe gani",
        "leo ni siku gani",
        "ni siku gani leo",
    ]

    if any(keyword in message for keyword in time_keywords):
        return "TIME_QUERY"


    # --------------------------------------------------------
    # 4. FISH INFORMATION
    # --------------------------------------------------------

    fish_keywords = [
        "fish",
        "samaki",
        "tilapia",
        "catfish",
        "sardine",
        "tuna",
        "salmon",
        "aquaculture",
        "fisheries",
        "fishing",
        "fish habitat",
        "fish diet",
        "fish biology",
        "samaki anaishi",
        "samaki anakula",
        "ufugaji wa samaki",
        "uvuvi",
    ]

    if any(keyword in message for keyword in fish_keywords):
        return "FISH_INFORMATION"


    # --------------------------------------------------------
    # 5. PROGRAMMING / TECHNOLOGY
    # --------------------------------------------------------

    technology_keywords = [
        "python",
        "javascript",
        "java",
        "react",
        "node.js",
        "nodejs",
        "fastapi",
        "api",
        "database",
        "mysql",
        "sql",
        "programming",
        "code",
        "coding",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "ai",
        "cnn",
        "yolo",
        "transformer",
        "computer vision",
        "rag",
        "agentic rag",
        "programu",
        "teknolojia",
    ]

    if any(keyword in message for keyword in technology_keywords):
        return "PROGRAMMING_OR_TECHNOLOGY"


    # --------------------------------------------------------
    # 6. NORMAL CONVERSATION
    # --------------------------------------------------------

    conversation_keywords = [
        "hello",
        "hi",
        "hey",
        "habari",
        "mambo",
        "shikamoo",
        "asante",
        "thanks",
        "thank you",
        "good morning",
        "good afternoon",
        "good evening",
    ]

    if any(keyword in message for keyword in conversation_keywords):
        return "CONVERSATION"


    # --------------------------------------------------------
    # 7. GENERAL KNOWLEDGE
    # --------------------------------------------------------

    return "GENERAL_KNOWLEDGE"

