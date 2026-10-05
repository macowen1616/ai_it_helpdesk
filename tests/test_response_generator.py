from backend.app.semantic_search import semantic_search
from backend.app.response_generator import generate_response


query = "My wireless connection keeps dropping"

results = semantic_search(query, top_k=3)

response = generate_response(query, results)

print("\nAI Helpdesk Response:")
print("=====================")
print(response)