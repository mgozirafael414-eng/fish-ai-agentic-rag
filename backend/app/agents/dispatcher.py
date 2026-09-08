# backend/app/agents/dispatcher.py


# ============================================================
# AGENT DISPATCHER
# ============================================================

AGENT_MAP = {
    "FISH_IDENTIFICATION": "Fish Identification Agent",
    "FISH_INFORMATION": "Fish Knowledge Agent",
    "DOCUMENT_QUERY": "RAG Retrieval Agent",
    "IMAGE_ANALYSIS": "Image Analysis Agent",
    "GENERAL_KNOWLEDGE": "General Knowledge Agent",
    "PROGRAMMING_OR_TECHNOLOGY": "Technology Agent",
    "CONVERSATION": "Conversation Agent",

    # TIME AGENT
    "TIME_QUERY": "Time Agent",
}


def dispatch_agent(route: str) -> str:
    """
    Select the agent responsible for handling a route.
    """

    agent = AGENT_MAP.get(
        route,
        "General Knowledge Agent"
    )

    print(
        f"[DISPATCHER] Route: {route}"
    )

    print(
        f"[DISPATCHER] Agent: {agent}"
    )

    return agent