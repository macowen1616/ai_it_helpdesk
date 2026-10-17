
import json
from pathlib import Path

from backend.app.semantic_search import semantic_search


PROJECT_DIR = Path(__file__).resolve().parents[1]
QUESTIONS_FILE = PROJECT_DIR / "research" / "test_questions.json"
RESULTS_FILE = PROJECT_DIR / "research" / "retrieval_evaluation_results.json"


def main():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    results = []
    correct = 0

    for question in questions:
        query = question["query"]
        expected = question["expected_document"]

        matches = semantic_search(query, top_k=1)
        actual = matches[0]["document"] if matches else None
        score = matches[0]["score"] if matches else 0.0

        passed = actual == expected
        correct += passed

        result = {
            "id": question["id"],
            "query": query,
            "expected_document": expected,
            "actual_document": actual,
            "score": score,
            "correct": passed,
        }
        results.append(result)

        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {query}")
        print(f"       Expected: {expected}")
        print(f"       Retrieved: {actual}")
        print(f"       Score: {score:.4f}")

    total = len(questions)
    accuracy = (correct / total * 100) if total else 0.0

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            {
                "total_questions": total,
                "correct": correct,
                "incorrect": total - correct,
                "accuracy_percent": accuracy,
                "results": results,
            },
            file,
            indent=2,
        )

    print("\n=== Retrieval Evaluation Summary ===")
    print(f"Total questions: {total}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {total - correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Detailed results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
