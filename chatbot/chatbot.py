"""Medicine lookup and safe response generation for the chatbot."""

import re

from database.db import get_connection
from ai.llm import DISCLAIMER, generate_ai_answer
from .intents import detect_intent, normalize_text


FIELD_BY_INTENT = {
    "USE": "general_uses",
    "SIDE_EFFECT": "side_effects",
    "WARNING": "warnings",
    "GENERIC_NAME": "generic_name",
    "CATEGORY": "category",
    "INGREDIENT": "ingredients",
    "STORAGE": "storage_information",
    "INTERACTION": "interaction_information",
    "GENERAL_INFORMATION": "category",
}

SAFETY_KEYWORDS = (
    "which medicine should i take",
    "what medicine should i take",
    "should i take",
    "diagnose",
    "diagnosis",
    "prescribe",
    "personal dosage",
    "how much should i take",
    "start taking",
    "stop taking",
    "change my medication",
    "emergency",
    "severe symptoms",
)


def with_disclaimer(answer):
    """Add the standard medical-information disclaimer when needed."""
    if DISCLAIMER in answer:
        return answer
    return f"{answer} {DISCLAIMER}"


def find_medicine(question, medicine_id=None):
    """Find a medicine by context ID first, then by name in the question."""
    connection = get_connection()
    medicine = None

    if medicine_id is not None:
        medicine = connection.execute(
            "SELECT * FROM medicines WHERE id = ?",
            (medicine_id,),
        ).fetchone()

    if medicine is None:
        normalized_question = normalize_text(question)
        medicines = connection.execute(
            "SELECT * FROM medicines ORDER BY length(name) DESC"
        ).fetchall()
        for candidate in medicines:
            medicine_names = (candidate["name"], candidate["generic_name"])
            for medicine_name in medicine_names:
                normalized_name = normalize_text(medicine_name)
                if re.search(rf"\b{re.escape(normalized_name)}\b", normalized_question):
                    medicine = candidate
                    break
            if medicine is not None:
                break

    connection.close()
    return medicine


def format_database_answer(medicine, intent):
    """Format stored medicine information as a clear, safe response."""
    medicine_name = medicine["name"]
    information = medicine[FIELD_BY_INTENT[intent]]

    if intent == "INGREDIENT":
        response = (
            f"Active ingredient in {medicine_name}: {information}.\n\n"
            "For the complete formulation, including any inactive ingredients, "
            "please check the specific product packaging or leaflet."
        )
    elif intent == "USE" and information.lower().startswith("used to "):
        response = f"{medicine_name} is {information[0].lower()}{information[1:]}"
    elif information.lower().startswith(medicine_name.lower()):
        response = information
    else:
        response_formats = {
            "INGREDIENT": f"The active ingredient in {medicine_name} is {information}.",
            "GENERIC_NAME": f"The generic name of {medicine_name} is {information}.",
            "USE": f"{medicine_name} is commonly used for {information}.",
            "WARNING": f"{medicine_name} warnings: {information}",
            "SIDE_EFFECT": f"Possible side effects of {medicine_name}: {information}",
            "STORAGE": f"Storage information for {medicine_name}: {information}",
            "INTERACTION": f"Interactions: {information}",
        }
        response = response_formats.get(intent, f"{medicine_name}: {information}")
    return f"{response} Please refer to the medicine label or consult a qualified doctor or pharmacist for advice specific to your situation."


def answer_question(question, medicine_id=None):
    """Classify a question, retrieve database content, and return a safe answer."""
    intent = detect_intent(question)

    if any(keyword in normalize_text(question) for keyword in SAFETY_KEYWORDS):
        return {
            "answer": with_disclaimer("I cannot diagnose, prescribe, or recommend personal medicine choices or doses. Please consult a qualified doctor or pharmacist for advice about your situation."),
            "medicine": None,
            "intent": "UNKNOWN",
        }

    medicine = find_medicine(question, medicine_id)
    if medicine is None:
        return {
            "answer": with_disclaimer("I couldn't find that medicine in the medicine information database. Please check the medicine name or search for a medicine in the database."),
            "medicine": None,
            "intent": intent,
        }

    if intent == "UNKNOWN":
        return {
            "answer": with_disclaimer("I couldn't confidently identify what you are asking. Please select a topic such as uses, side effects, warnings, ingredients, storage, or interactions."),
            "medicine": medicine["name"],
            "intent": intent,
        }

    # AI receives only the matched database record; the local answer remains the fallback.
    ai_answer = generate_ai_answer(question, medicine)
    return {
        "answer": ai_answer or format_database_answer(medicine, intent),
        "medicine": medicine["name"],
        "intent": intent,
    }
