import re


def clean_text(text: str):

    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n+", "\n", text)

    text = text.replace("|", " | ")

    return text.strip()