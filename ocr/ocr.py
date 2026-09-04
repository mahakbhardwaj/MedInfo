"""Small OCR module for reading medicine package text."""

import re
from io import BytesIO

import pytesseract
from PIL import Image, UnidentifiedImageError


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
}

OCR_BRAND_ALIASES = {
    "combiflam": ("ibuprofen", "paracetamol"),
}


def allowed_image(filename, mimetype):
    """Check the filename extension and browser-provided MIME type."""
    extension = (
        filename.rsplit(".", 1)[-1].lower()
        if "." in filename
        else ""
    )

    return (
        extension in ALLOWED_EXTENSIONS
        and mimetype in ALLOWED_MIME_TYPES
    )


def extract_text(image_bytes):
    """Validate image bytes with Pillow and extract text with Tesseract."""
    try:
        image = Image.open(BytesIO(image_bytes))
        image.load()
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError(
            "The uploaded file is not a valid image."
        ) from error

    text = pytesseract.image_to_string(image)

    return re.sub(r"\s+", " ", text).strip()


def identify_medicine(text, medicines):
    """Identify a medicine from OCR text."""
    normalized_text = re.sub(
        r"\s+",
        " ",
        text.lower()
    ).strip()

    # Check OCR-only brand aliases first.
    for brand_name, ingredient_names in OCR_BRAND_ALIASES.items():
        compact_text = re.sub(
            r"[\s-]+",
            "",
            normalized_text
        )

        compact_brand = re.sub(
            r"[\s-]+",
            "",
            brand_name
        )

        if compact_brand not in compact_text:
            continue

        ingredient_records = {
            medicine["name"].lower(): medicine
            for medicine in medicines
            if medicine["name"].lower() in ingredient_names
        }

        if all(
            name in ingredient_records
            for name in ingredient_names
        ):
            matched_medicine = dict(
                ingredient_records[ingredient_names[0]]
            )

            matched_medicine["name"] = "Combiflam"
            matched_medicine["generic_name"] = (
                "Ibuprofen + Paracetamol"
            )
            matched_medicine["ingredients"] = (
                "Ibuprofen + Paracetamol"
            )

            return matched_medicine

    # Existing medicine-name/generic-name matching.
    for medicine in medicines:
        for name in (
            medicine["name"],
            medicine["generic_name"]
        ):
            normalized_name = re.sub(
                r"\s+",
                " ",
                name.lower()
            ).strip()

            if re.search(
                rf"\b{re.escape(normalized_name)}\b",
                normalized_text
            ):
                return medicine

    return None