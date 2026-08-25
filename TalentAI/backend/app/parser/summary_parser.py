import re


def clean_summary(text: str) -> str:
    """
    Clean extracted summary text.
    """

    if not text:
        return ""

    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def extract_summary(text: str):
    """
    Extract the complete professional summary.
    """

    text = clean_summary(text)

    if not text:
        return None

    return text


def normalize_summary(summary):
    """
    Normalize summary text without changing its meaning.
    """

    if not summary:
        return None

    summary = " ".join(summary.split())

    return summary.strip()


def parse_summary(text: str):

    if not text:
        return None

    summary = extract_summary(text)

    summary = normalize_summary(summary)

    return summary