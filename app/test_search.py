from embeddings.embedder import Embedder
from vector_store.vector_store import VectorStore


documents = [
    "The login function checks the user's password.",
    "The database stores user information.",
    "The weather API returns temperature data.",
    "Authentication verifies the identity of a user."
]


embedder = Embedder()

vectors = embedder.embed_many(documents)

store = VectorStore()

store.add(vectors, documents)


query = "How does user authentication work?"

query_vector = embedder.embed(query)

results = store.search(query_vector, top_k=2)


for result in results:
    print("\nDocument:")
    print(result["document"])

    print("Similarity:")
    print(result["similarity"])