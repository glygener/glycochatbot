import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "glygen-chatbot"))

from RAG.pipeline import RAGPipeline  # noqa: E402


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("Ask a glycobiology question: ").strip()
    if not question:
        print("No question provided.")
        sys.exit(1)

    pipeline = RAGPipeline()
    response = pipeline.ask(question)
    print(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    main()
