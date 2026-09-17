from typing import List, Dict

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


# ============================================================
# EMBEDDING MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# EMBEDDING SERVICE
# ============================================================

class EmbeddingService:

    def __init__(
        self,
        model_name: str = MODEL_NAME
    ):

        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name
        )

    # ========================================================
    # GENERATE SINGLE EMBEDDING
    # ========================================================

    def generate_embedding(
        self,
        text: str
    ):

        if not text:

            return []

        embedding = self.model.encode(
            text,
            convert_to_tensor=True
        )

        return embedding

    # ========================================================
    # GENERATE MULTIPLE EMBEDDINGS
    # ========================================================

    def generate_embeddings(
        self,
        texts: List[str]
    ):

        if not texts:

            return []

        embeddings = self.model.encode(
            texts,
            convert_to_tensor=True
        )

        return embeddings

    # ========================================================
    # CALCULATE SIMILARITY
    # ========================================================

    def calculate_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:

        if not text1 or not text2:

            return 0.0

        embedding1 = self.generate_embedding(
            text1
        )

        embedding2 = self.generate_embedding(
            text2
        )

        similarity = cos_sim(
            embedding1,
            embedding2
        )

        return round(
            float(similarity.item()),
            4
        )

    # ========================================================
    # FIND MOST SIMILAR CANDIDATE
    # ========================================================

    def find_most_similar(
        self,
        query: str,
        candidates: List[str]
    ) -> Dict:

        if not query:

            return {
                "query": query,
                "match": None,
                "similarity": 0.0
            }

        if not candidates:

            return {
                "query": query,
                "match": None,
                "similarity": 0.0
            }

        query_embedding = self.generate_embedding(
            query
        )

        candidate_embeddings = self.generate_embeddings(
            candidates
        )

        similarities = cos_sim(
            query_embedding,
            candidate_embeddings
        )[0]

        best_index = int(
            similarities.argmax().item()
        )

        best_similarity = round(
            float(
                similarities[best_index].item()
            ),
            4
        )

        return {
            "query": query,
            "match": candidates[best_index],
            "similarity": best_similarity
        }