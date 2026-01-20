from typing import List
import re
import spacy
from langsmith import traceable

REGEX_PATTERNS: List[tuple[str, str]] = [
    (r"\b[\w.-]+@[\w.-]+\.\w+\b", "[REDACTED]"),
    (r"\b(?:\+?\d{1,3})?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b", "[REDACTED]"),
    (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[REDACTED]"),
    (r"\bORD-\d{6,8}\b", "[REDACTED]"),
]

nlp = spacy.load("en_core_web_md", disable=["tagger", "parser", "lemmatizer"])

@traceable
def redact(text: str) -> str:
    """
    Redacts sensitive information (Personally Identifiable Information - PII) from a given text.

    This function performs redaction in two main steps:
    1.  **Regex-based Redaction:** Applies a predefined set of regular expressions
        to identify and replace common patterns like email addresses, phone numbers,
        credit card numbers, and specific order IDs with generic '[REDACTED]' placeholders.
    2.  **Named Entity Recognition (NER) Redaction:** Uses the spaCy library to
        identify and redact specific types of named entities from the text,
        including:
        -   **LOC** (Geographical locations)
        -   **PERSON** (People's names)
        -   **GPE** (Geopolitical entities like countries, cities, states)
        Entities are processed in reverse ord
        er to avoid issues with changing
        string indices during redaction.

    Args:
        text (str): The input text (e.g., customer email) from which PII needs to be redacted.

    Returns:
        str: The redacted text with identified PII replaced by '[REDACTED]' placeholders.
    """
    for pattern, repl in REGEX_PATTERNS:
        text = re.sub(pattern, repl, text, flags=re.I)
    doc = nlp(text)
    for ent in reversed(doc.ents):
        if ent.label_ in {"LOC", "PERSON", "GPE", "NORP", "FAC"}:
            text = text[:ent.start_char] + f"[REDACTED]" + text[ent.end_char:]
    return text

