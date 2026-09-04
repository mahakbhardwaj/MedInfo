"""Optional OpenAI integration with a database-backed fallback."""

import os

from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:  # Keep the local chatbot usable before dependencies are installed.
    OpenAI = None


load_dotenv()


SYSTEM_PROMPT = """You are a medicine information assistant.

Provide general educational information only.

Use only the medicine information supplied by the application.

Do not diagnose diseases.

Do not prescribe medicines.

Do not recommend changing dosage.

Do not tell users to start, stop, or change medication.

Do not invent missing medical information.

If the requested information is not present in the supplied medicine record, clearly say that the information is not available in the application's database.

For urgent or personal medical concerns, advise the user to consult a qualified doctor or pharmacist.

Keep the answer short, clear, and beginner-friendly.

Do not add an introductory phrase before database text that already contains
natural wording. For example, if the database says "Used to relieve pain and
reduce fever.", write "Paracetamol is used to relieve pain and reduce fever."
Do not write "Paracetamol is commonly used for Used to relieve pain and reduce
fever." Do not repeat database text or labels.

End every answer with this exact disclaimer: "This is general medical information, not a diagnosis or medical advice. Consult a qualified doctor or pharmacist for advice specific to your situation."
"""

DISCLAIMER = "This is general medical information, not a diagnosis or medical advice. Consult a qualified doctor or pharmacist for advice specific to your situation."


def create_medicine_context(medicine):
    """Select only the medicine fields needed by the AI request."""
    return "\n".join([
        f"Medicine: {medicine['name']}",
        f"Generic name: {medicine['generic_name']}",
        f"Category: {medicine['category']}",
        f"Uses: {medicine['general_uses']}",
        f"Warnings: {medicine['warnings']}",
        f"Side effects: {medicine['side_effects']}",
        f"Ingredients: {medicine['ingredients']}",
        f"Storage: {medicine['storage_information']}",
        f"Interactions: {medicine['interaction_information']}",
    ])


def generate_ai_answer(question, medicine):
    """Return an AI answer, or None when optional AI is unavailable."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or OpenAI is None:
        return None

    model = os.environ.get("AI_MODEL", "gpt-4o-mini")

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=180,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"{create_medicine_context(medicine)}\n\nUser question: {question}",
                },
            ],
        )
        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            return None
        if DISCLAIMER not in answer:
            answer = f"{answer}\n\n{DISCLAIMER}"
        return answer
    except Exception:
        return None
