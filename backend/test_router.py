from app.router_agent import route_query


test_questions = [
    "What is tilapia?",
    "Where does catfish live?",
    "Identify this fish",
    "Tambua aina ya samaki huyu",
    "According to the PDF, what is aquaculture?",
    "What is Python?",
    "Explain machine learning",
    "Hello FishAI",
    "What is photosynthesis?",
]


for question in test_questions:

    result = route_query(question)

    print(
        f"Question: {question}"
    )

    print(
        f"Route: {result}"
    )

    print("-" * 60)