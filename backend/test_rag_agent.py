import asyncio

from app.agents.rag_agent import rag_agent


async def main():

    query = "What do tilapia eat?"

    print("=" * 60)
    print("RAG AGENT TEST")
    print("=" * 60)

    print()
    print("Question:")
    print(query)

    print()
    print("Generating answer...")

    answer = await rag_agent(
        user_message=query,
        conversation=[],
        n_results=3,
    )

    print()
    print("=" * 60)
    print("RAG ANSWER")
    print("=" * 60)

    print()
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())