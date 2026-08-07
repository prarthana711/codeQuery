import faiss
import numpy as np


class FAISSVectorStore:

    def __init__(self, dim=384):
        self.dim = dim
        # Inner product on L2-normalized vectors == cosine similarity.
        # Cosine similarity is more interpretable than raw L2 distance:
        # scores land in [-1, 1], where 1.0 means identical direction.
        self.index = faiss.IndexFlatIP(dim)
        self.documents = []

    def reset(self):
        self.index = faiss.IndexFlatIP(self.dim)
        self.documents = []

    def _normalize(self, vectors):
        vectors = np.array(vectors).astype("float32")
        faiss.normalize_L2(vectors)
        return vectors

    def add(self, vectors, documents):
        vectors = self._normalize(vectors)
        self.index.add(vectors)
        self.documents.extend(documents)

    def search(self, query_vector, k=5, min_score=0.3):
        """
        Return up to k documents most similar to query_vector, dropping any
        below min_score. This threshold matters: without it, a search always
        returns k results even when nothing in the repo is actually relevant,
        which forces the LLM to answer from irrelevant context and invites
        hallucination. 0.3 is a reasonable starting point for MiniLM cosine
        similarity — tune it against your own repos if answers feel too
        sparse (lower it) or too noisy (raise it).
        """
        query_vector = self._normalize([query_vector])
        scores, indices = self.index.search(query_vector, k)

        results = []
        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue
            if score < min_score:
                continue

            results.append({
                "document": self.documents[index],
                "similarity": float(score),
            })

        return results