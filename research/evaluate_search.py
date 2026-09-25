import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from backend.app.search import search_documents


QUESTIONS_FILE = BASE_DIR / "research" / "test_questions.json"

def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_search():
    questions = load_questions()

    correct = 0
    results = []

    for question in questions:
        query = question["query"]
        expected_document = question["expected_document"]

        search_results = search_documents(query)

        if search_results:
            actual_document = search_results[0]["document"]
        else:
            actual_document = None

        is_correct = actual_document == expected_document

        if is_correct:
            correct += 1

        results.append(
            {
                "id": question["id"],
                "query": query,
                "expected": expected_document,
                "actual": actual_document,
                "correct": is_correct,
            }
        )

    total = len(questions)
    accuracy = (correct / total) * 100 if total else 0

    print("\nSearch Evaluation")
    print("-----------------")
    print(f"Total questions: {total}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {total - correct}")
    print(f"Accuracy: {accuracy:.2f}%")

    print("\nDetailed Results")
    print("----------------")

    for result in results:
        status = "CORRECT" if result["correct"] else "INCORRECT"

        print(
            f"{result['id']}. {status} | "
            f"{result['query']} | "
            f"Expected: {result['expected']} | "
            f"Actual: {result['actual']}"
        )


if __name__ == "__main__":
    evaluate_search()