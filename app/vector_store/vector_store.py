import numpy as np


class VectorStore:

    def __init__(self):
        self.vectors = []
        self.documents = []

    def add(self, vectors, documents):
        self.vectors.extend(vectors)
        self.documents.extend(documents)

    def search(self, query_vector, top_k=3):
        query_vector = np.array(query_vector)

        similarities = []

        for vector in self.vectors:
            vector = np.array(vector)

            similarity = np.dot(query_vector, vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(vector)
            )

            similarities.append(similarity)

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []

        for index in top_indices:
            results.append({
                "document": self.documents[index],
                "similarity": similarities[index]
            })

        return results