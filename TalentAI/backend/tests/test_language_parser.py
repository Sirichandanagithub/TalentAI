from app.parser.language_parser import parse_languages


# ============================================================
# TEST LANGUAGE PARSER
# ============================================================

language_text = """
English - Fluent
Hindi (Intermediate)
Telugu: Native
"""


result = parse_languages(language_text)


print()
print("# LANGUAGES")
print()

print("RESULT:", result)

print()

print(
    "Number of languages:",
    len(result)
)

for index, language in enumerate(
    result,
    start=1
):

    print()
    print(f"[{index}]")

    print(
        "Language    :",
        language["language"]
    )

    print(
        "Proficiency :",
        language.get(
            "proficiency",
            None
        )
    )


print()
print("TEST FILE FINISHED")