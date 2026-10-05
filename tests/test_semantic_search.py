from backend.app.semantic_search import semantic_search

queries = [
    "My wireless connection keeps dropping",
    "I can't remember my computer login credentials",
    "The VPN won't establish a connection from home",
    "I need permission to download and install a program",
    "The printer is connected but nothing is coming out",
    "Messages are stuck and won't send from Outlook",
    "My computer says it is connected but I have no internet",
    "I am working remotely and cannot access the company network",
]

for query in queries:
    print(f"\nQuery: {query}")

    results = semantic_search(query, top_k=3)

    for result in results:
        print(f"  {result['document']} - score: {result['score']:.4f}")