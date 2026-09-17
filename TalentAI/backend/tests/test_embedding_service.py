from app.ai.embeddings.embedding_service import (
    EmbeddingService
)


# ============================================================
# INITIALIZE SERVICE
# ============================================================

print("=" * 60)
print("INITIALIZING EMBEDDING SERVICE")
print("=" * 60)

service = EmbeddingService()

print("Embedding model loaded successfully.")


# ============================================================
# TEST 1: EXACT / VERY SIMILAR CONCEPT
# ============================================================

print("\n" + "=" * 60)
print("TEST 1: MACHINE LEARNING")
print("=" * 60)

similarity = service.calculate_similarity(
    "Machine Learning",
    "Machine Learning"
)

print(
    "Machine Learning ↔ Machine Learning:",
    similarity
)


# ============================================================
# TEST 2: RELATED CONCEPT
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: RELATED CONCEPT")
print("=" * 60)

similarity = service.calculate_similarity(
    "Machine Learning",
    "Classification"
)

print(
    "Machine Learning ↔ Classification:",
    similarity
)


# ============================================================
# TEST 3: ANOTHER RELATED CONCEPT
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: PREDICTIVE MODELING")
print("=" * 60)

similarity = service.calculate_similarity(
    "Machine Learning",
    "Predictive modeling"
)

print(
    "Machine Learning ↔ Predictive modeling:",
    similarity
)


# ============================================================
# TEST 4: UNRELATED CONCEPT
# ============================================================

print("\n" + "=" * 60)
print("TEST 4: UNRELATED CONCEPT")
print("=" * 60)

similarity = service.calculate_similarity(
    "Machine Learning",
    "Graphic Design"
)

print(
    "Machine Learning ↔ Graphic Design:",
    similarity
)


# ============================================================
# TEST 5: FIND MOST SIMILAR
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: FIND MOST SIMILAR")
print("=" * 60)

candidates = [
    "Graphic Design",
    "Classification",
    "Accounting",
    "Machine Learning",
    "Marketing"
]

result = service.find_most_similar(
    "Machine Learning",
    candidates
)

print(result)


# ============================================================
# TEST 6: SQL SEMANTIC SEARCH
# ============================================================

print("\n" + "=" * 60)
print("TEST 6: SQL SEMANTIC SEARCH")
print("=" * 60)

candidates = [
    "Python",
    "MySQL",
    "MongoDB",
    "HTML",
    "Graphic Design"
]

result = service.find_most_similar(
    "SQL",
    candidates
)

print(result)


# ============================================================
# TEST 7: DATA SCIENCE SEMANTIC SEARCH
# ============================================================

print("\n" + "=" * 60)
print("TEST 7: DATA SCIENCE SEMANTIC SEARCH")
print("=" * 60)

candidates = [
    "Frontend Development",
    "Data Analysis",
    "Machine Learning",
    "Graphic Design",
    "Video Editing"
]

result = service.find_most_similar(
    "Data Science",
    candidates
)

print(result)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("EMBEDDING SERVICE TEST FINISHED")
print("=" * 60)