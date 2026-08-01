from app.ingestion.read_repo import read_repository
from app.chunking.chunker import chunk_documents
from app.pipeline.pipeline import Pipeline
from app.llm.llm import LLM

repo_path = "repositories/repo"

print("Reading repository...")
documents = read_repository(repo_path)

print(f"Files read: {len(documents)}")

print("Chunking documents...")
chunked_documents = chunk_documents(documents)

print(f"Chunks created: {len(chunked_documents)}")

pipeline = Pipeline()
llm = LLM()

print("Generating embeddings...")
pipeline.build(chunked_documents)

print("\nRepository indexed successfully!")

while True:

    question = input("\nAsk a question (or type 'exit'): ")

    if question.lower() == "exit":
        break

    results = pipeline.search(question)

    print("\nRetrieved Chunks:\n")

    for i, result in enumerate(results, start=1):

        print(f"\nChunk {i}")

        print("File:", result["document"]["path"])

        print("Score:", round(result["similarity"], 3))

        print(result["document"]["content"][:200])

        print("-" * 50)

    answer = llm.generate(question, results)

    print("\n" + "=" * 60)
    print("Answer:")
    print("=" * 60)
    print(answer)