import faiss
import numpy as np


class FAISSVectorStore:

    def __init__(self):
        # Create a FAISS index for vectors of dimension 384
        self.index = faiss.IndexFlatL2(384)

        # Store the corresponding documents (metadata)
        self.documents = []

    def reset(self):
        """
        Clear the current index and stored documents.
        """

        self.index = faiss.IndexFlatL2(384)

        self.documents = []

    def add(self, vectors, documents):
        """
        Add vectors and their corresponding documents to the index.
        """

        # Convert list of vectors to NumPy array
        vectors = np.array(vectors)

        # FAISS expects float32
        vectors = vectors.astype("float32")

        # Add vectors to the FAISS index
        self.index.add(vectors)

        # Store the corresponding documents
        self.documents.extend(documents)

    def search(self, query_vector, k=3):
        """
        Search for the k most similar documents.
        """

        # Convert query vector to NumPy array
        query_vector = np.array([query_vector]).astype("float32")

        # Search the index
        distances, indices = self.index.search(query_vector, k)

        results = []

        # Build the result list
        for i, index in enumerate(indices[0]):

            # Skip invalid indices (can happen if there are fewer than k vectors)
            if index == -1:
                continue

            results.append({
                "document": self.documents[index],
                "similarity": float(distances[0][i])
            })

        return results