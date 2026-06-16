import re


def clean_transcript(text: str) -> str:
    """Removes noise from transcript text."""

    text = re.sub(r"\[.*?\]", "", text)

    text = re.sub(r"\(.*?\)", "", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()