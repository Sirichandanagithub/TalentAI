from app.ai.analyzer.skill_relationship_engine import SkillRelationshipEngine


def print_result(title, result):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(result)


def main():

    engine = SkillRelationshipEngine()

    # ---------------------------------------------------------
    # TEST 1 — Strong relationship
    # ---------------------------------------------------------
    result = engine.find_relationship(
        "TensorFlow",
        "Deep Learning"
    )

    print_result(
        "TEST 1: TensorFlow ↔ Deep Learning",
        result
    )

    # ---------------------------------------------------------
    # TEST 2 — Related relationship
    # ---------------------------------------------------------
    result = engine.find_relationship(
        "TensorFlow",
        "Machine Learning"
    )

    print_result(
        "TEST 2: TensorFlow ↔ Machine Learning",
        result
    )

    # ---------------------------------------------------------
    # TEST 3 — SQL relationship
    # ---------------------------------------------------------
    result = engine.find_relationship(
        "PostgreSQL",
        "SQL"
    )

    print_result(
        "TEST 3: PostgreSQL ↔ SQL",
        result
    )

    # ---------------------------------------------------------
    # TEST 4 — Data Science relationship
    # ---------------------------------------------------------
    result = engine.find_relationship(
        "Data Science",
        "Machine Learning"
    )

    print_result(
        "TEST 4: Data Science ↔ Machine Learning",
        result
    )

    # ---------------------------------------------------------
    # TEST 5 — Pandas relationship
    # ---------------------------------------------------------
    result = engine.find_relationship(
        "Pandas",
        "Data Analysis"
    )

    print_result(
        "TEST 5: Pandas ↔ Data Analysis",
        result
    )

    # ---------------------------------------------------------
    # TEST 6 — Unrelated skills
    # ---------------------------------------------------------
    result = engine.find_relationship(
        "TensorFlow",
        "SQL"
    )

    print_result(
        "TEST 6: TensorFlow ↔ SQL",
        result
    )

    # ---------------------------------------------------------
    # TEST 7 — Find all related skills
    # ---------------------------------------------------------
    result = engine.find_related_skills(
        "Machine Learning"
    )

    print_result(
        "TEST 7: Related skills for Machine Learning",
        result
    )

    # ---------------------------------------------------------
    # TEST 8 — Reverse relationship
    # ---------------------------------------------------------
    result = engine.find_relationship(
        "Deep Learning",
        "TensorFlow"
    )

    print_result(
        "TEST 8: Reverse relationship",
        result
    )


if __name__ == "__main__":
    main()