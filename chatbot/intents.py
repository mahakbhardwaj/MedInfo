"""Keyword-based intent detection for the beginner chatbot."""

import re


INTENT_KEYWORDS = {
    "USE": ("used for", "what does it do", "what does", "purpose", "why is it used", "why is it taken", "why is this medicine", "what does it treat", "use"),
    "WARNING": (
        "warning", "warnings", "caution", "precaution", "precautions", "danger",
        "what should i know before taking", "what should i know before using",
        "things to know before taking", "things to know before using",
        "what should i be careful about", "what should i know about taking",
        "precautions before taking", "is it safe to take", "is it safe to use",
        "when should i avoid", "what should i avoid",
    ),
    "SIDE_EFFECT": ("side effect", "side effects", "adverse effect", "adverse effects", "reaction"),
    "STORAGE": ("storage", "store", "stored", "keep", "temperature"),
    "INTERACTION": ("interaction", "interactions", "interact", "other medicine", "other medicines", "drug interaction"),
    "INGREDIENT": ("ingredient", "ingredients", "active ingredient", "composition"),
    "GENERIC_NAME": ("generic name",),
    "CATEGORY": ("category", "class of medicine", "type of medicine"),
}


def normalize_text(text):
    """Lowercase text and replace punctuation with spaces."""
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).strip()


def detect_intent(question):
    """Return the highest-scoring supported intent for the question."""
    normalized_question = normalize_text(question)

    best_intent = None
    best_score = 0
    best_keyword_length = 0

    for intent, keywords in INTENT_KEYWORDS.items():
        matching_keywords = [
            keyword
            for keyword in keywords
            if re.search(rf"\b{re.escape(keyword)}\b", normalized_question)
        ]
        score = len(matching_keywords)
        longest_keyword_length = max(
            (len(keyword) for keyword in matching_keywords),
            default=0,
        )

        if (score, longest_keyword_length) > (best_score, best_keyword_length):
            best_intent = intent
            best_score = score
            best_keyword_length = longest_keyword_length

    if best_intent is not None:
        return best_intent

    if normalized_question.startswith("what is"):
        return "GENERAL_INFORMATION"

    return "UNKNOWN"
