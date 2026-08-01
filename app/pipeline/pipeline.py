from app.embeddings.embedder import Embedder
from app.vector_store.faiss_store import FAISSVectorStore


class Pipeline:

    def __init__(self):

        self.embedder = Embedder()

        self.store = FAISSVectorStore()

    def build(self, documents):

        texts = []

        for doc in documents:
            texts.append(doc["content"])

        vectors = self.embedder.embed_many(texts)

        self.store.add(vectors, documents)

        print(f"Indexed {len(documents)} chunks")

    def search(self, question):

        query_vector = self.embedder.embed(question)

        return self.store.search(query_vector)