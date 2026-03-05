"""Classification route — POST /api/classify."""

import logging
import os

from flask import Blueprint, jsonify, request, session

from backend import gemini_service, ml_classifier
from backend.grading_engine import compute_grade
from backend.config import Config

logger = logging.getLogger(__name__)
classify_bp = Blueprint("classify", __name__)

ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
MAX_HISTORY_SIZE = 50


def _allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@classify_bp.route("/api/classify", methods=["POST"])
def classify():
    """Classify a rock/mineral/ore sample.

    Accepts:
        - multipart/form-data with 'image' file
        - JSON or form field 'description' (text only)

    Returns:
        JSON classification result.
    """
    image_bytes = None
    description = request.form.get("description", "") or (
        request.json.get("description", "") if request.is_json else ""
    )

    # --- Image upload ---
    if "image" in request.files:
        file = request.files["image"]
        if file.filename and _allowed_file(file.filename):
            image_bytes = file.read()
            if len(image_bytes) > Config.MAX_CONTENT_LENGTH:
                return jsonify({"error": "File too large (max 16MB)"}), 413
        else:
            return jsonify({"error": "Invalid file type"}), 400

    if not image_bytes and not description:
        return jsonify({"error": "Provide an image or description"}), 400

    # --- Gemini analysis ---
    result = None
    try:
        if image_bytes:
            result = gemini_service.analyze_image(image_bytes, description)
        else:
            result = gemini_service.analyze_description(description)
    except Exception as exc:
        logger.warning("Gemini API failed: %s. Falling back to ML classifier.", exc)

    # --- ML fallback ---
    if result is None:
        result = ml_classifier.classify_features(
            color=description[:20] if description else "gray",
            purity_percentage=60.0,
        )

    # --- Ensure grade is consistent with purity ---
    purity = float(result.get("purity_percentage", 60))
    grade_info = compute_grade(purity)
    result["quality_grade"] = grade_info["grade"]
    result["grade_color"] = grade_info["color"]
    result["grade_label"] = grade_info["label"]

    # Ensure lists are lists
    for key in ("primary_elements", "associated_minerals", "industrial_uses"):
        if isinstance(result.get(key), str):
            result[key] = [x.strip() for x in result[key].split(",") if x.strip()]
        elif not isinstance(result.get(key), list):
            result[key] = []

    # Store in session for result page and history
    session["last_result"] = result
    history = session.setdefault("analyses_history", [])
    history.append(result)
    if len(history) > MAX_HISTORY_SIZE:
        history[:] = history[-MAX_HISTORY_SIZE:]
    session.modified = True

    return jsonify(result)
