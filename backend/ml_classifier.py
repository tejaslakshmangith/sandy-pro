"""scikit-learn ML classifier — fallback when Gemini API is unavailable."""

import logging
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from backend.config import Config
from backend.grading_engine import compute_grade

logger = logging.getLogger(__name__)

# Encoders (populated on first load)
_model = None
_label_encoders: dict = {}
_target_encoder = None


# ---------------------------------------------------------------------------
# Encoding helpers
# ---------------------------------------------------------------------------

COLOR_MAP = {
    "red": 0, "orange": 1, "yellow": 2, "green": 3, "blue": 4,
    "purple": 5, "brown": 6, "black": 7, "white": 8, "gray": 9,
    "silver": 10, "gold": 11, "pink": 12, "colorless": 13, "multicolor": 14,
}

LUSTER_MAP = {
    "metallic": 0, "vitreous": 1, "resinous": 2, "waxy": 3, "pearly": 4,
    "silky": 5, "adamantine": 6, "dull": 7, "earthy": 8, "submetallic": 9,
}

FORMATION_MAP = {
    "igneous": 0, "sedimentary": 1, "metamorphic": 2, "hydrothermal": 3,
    "evaporite": 4, "placer": 5,
}


def _encode_color(color: str) -> int:
    color_lower = str(color).lower()
    for key, val in COLOR_MAP.items():
        if key in color_lower:
            return val
    return 14  # multicolor / unknown


def _encode_luster(luster: str) -> int:
    luster_lower = str(luster).lower()
    for key, val in LUSTER_MAP.items():
        if key in luster_lower:
            return val
    return 7  # dull / unknown


def _encode_formation(formation: str) -> int:
    formation_lower = str(formation).lower()
    for key, val in FORMATION_MAP.items():
        if key in formation_lower:
            return val
    return 0  # igneous / unknown


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def _load_model():
    """Load the trained model from disk, or train a new one if not found."""
    global _model
    if _model is not None:
        return _model

    model_path = Config.ML_MODEL_PATH
    if os.path.exists(model_path):
        try:
            _model = joblib.load(model_path)
            logger.info("ML classifier loaded from %s", model_path)
            return _model
        except Exception as exc:
            logger.warning("Failed to load model: %s. Training fresh model.", exc)

    # Train a new model on the fly
    _model = _train_from_dataset()
    return _model


def _train_from_dataset() -> RandomForestClassifier:
    """Train a RandomForestClassifier from the minerals dataset."""
    dataset_path = Config.DATASET_PATH
    if not os.path.exists(dataset_path):
        logger.warning("Dataset not found at %s. Using dummy classifier.", dataset_path)
        return _dummy_classifier()

    df = pd.read_csv(dataset_path)

    df["color_code"] = df["color"].apply(_encode_color)
    df["luster_code"] = df["luster"].apply(_encode_luster)
    df["formation_code"] = df["formation_type"].apply(_encode_formation)
    df["hardness"] = pd.to_numeric(df["hardness_mohs"], errors="coerce").fillna(5.0)

    features = ["color_code", "hardness", "luster_code", "formation_code"]
    target = "category"

    X = df[features].values
    y = df[target].values

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)

    # Save for future use
    os.makedirs(os.path.dirname(Config.ML_MODEL_PATH), exist_ok=True)
    try:
        joblib.dump(clf, Config.ML_MODEL_PATH)
        logger.info("ML classifier saved to %s", Config.ML_MODEL_PATH)
    except Exception as exc:
        logger.warning("Could not save model: %s", exc)

    return clf


def _dummy_classifier():
    """Return a simple fallback classifier trained on synthetic data."""
    X = np.array([
        [7, 7.0, 1, 0],  # ore
        [0, 3.5, 0, 3],  # mineral
        [6, 6.0, 7, 0],  # rock
    ])
    y = ["ore", "mineral", "rock"]
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X, y)
    return clf


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_features(
    color: str = "gray",
    hardness: float = 5.0,
    luster: str = "vitreous",
    formation_type: str = "igneous",
    purity_percentage: float = 60.0,
) -> dict:
    """Classify a sample using ML features.

    Args:
        color: Color of the sample.
        hardness: Mohs hardness (1–10).
        luster: Luster type.
        formation_type: Geological formation type.
        purity_percentage: Estimated purity (0–100).

    Returns:
        Classification dict with category, grade, and basic properties.
    """
    model = _load_model()

    color_code = _encode_color(color)
    luster_code = _encode_luster(luster)
    formation_code = _encode_formation(formation_type)
    hard = float(hardness)

    features = np.array([[color_code, hard, luster_code, formation_code]])
    category = model.predict(features)[0]

    grade_info = compute_grade(purity_percentage)

    return {
        "category": category,
        "specific_name": "Unknown Sample",
        "common_name": "",
        "chemical_formula": "N/A",
        "color_description": color,
        "texture": "unknown",
        "luster": luster,
        "hardness_mohs": hard,
        "purity_percentage": purity_percentage,
        "quality_grade": grade_info["grade"],
        "commercial_value": _purity_to_commercial(purity_percentage),
        "mining_suitability": "open-pit",
        "primary_elements": [],
        "associated_minerals": [],
        "formation_type": formation_type,
        "geological_age": "Unknown",
        "industrial_uses": [],
        "confidence_score": 55,
        "analysis_notes": (
            "Classification performed by local ML model (Gemini API unavailable). "
            "Results may be less accurate than AI analysis."
        ),
        "extraction_difficulty": "moderate",
        "environmental_impact": "moderate",
        "market_value_usd_per_ton": 0,
        "recommended_processing": "crushing",
        "source": "ml_classifier",
    }


def _purity_to_commercial(purity: float) -> str:
    if purity >= 85:
        return "premium"
    if purity >= 70:
        return "high"
    if purity >= 55:
        return "medium"
    if purity >= 35:
        return "low"
    return "marginal"
