"""Roboflow ore_dataset service.

Uses the Roboflow hosted classification API to identify ore/mineral classes:
  hematite, ilmenite, limonite, magnetite, pyrite, rock
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any

import requests

from backend.config import Config

logger = logging.getLogger(__name__)

# Roboflow classification endpoint template
_INFER_URL = (
    "https://classify.roboflow.com/{project}/{version}"
    "?api_key={api_key}"
)

# Load class metadata from the reference JSON file
_ORE_DATASET_PATH = Path(__file__).parent.parent / "data" / "ore_dataset_classes.json"
with _ORE_DATASET_PATH.open() as _f:
    _ORE_DATASET = json.load(_f)

# Build class lookup: name → metadata dict
_CLASS_META: dict[str, dict] = {
    cls["name"]: {
        "full_name": cls["name"].capitalize() if cls["name"] != "rock" else "Rock / Unclassified",
        "formula": cls["formula"],
        "category": cls["category"],
        "commercial_value": cls["commercial_value"],
    }
    for cls in _ORE_DATASET["classes"]
}
# Override display names for multi-word minerals
_CLASS_META["hematite"]["full_name"] = "Hematite"
_CLASS_META["ilmenite"]["full_name"] = "Ilmenite"
_CLASS_META["limonite"]["full_name"] = "Limonite"
_CLASS_META["magnetite"]["full_name"] = "Magnetite"
_CLASS_META["pyrite"]["full_name"] = "Pyrite"


def classify_image(image_bytes: bytes) -> dict[str, Any] | None:
    """Send *image_bytes* to the Roboflow hosted classifier.

    Returns a result dict compatible with the existing classify pipeline,
    or *None* on failure so the caller can fall back gracefully.
    """
    api_key = Config.ROBOFLOW_API_KEY
    if not api_key:
        logger.warning("ROBOFLOW_API_KEY not set — skipping Roboflow inference.")
        return None

    try:
        # Roboflow classification API accepts base64-encoded image in the body
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        url = _INFER_URL.format(
            project=Config.ROBOFLOW_PROJECT,
            version=Config.ROBOFLOW_VERSION,
            api_key=api_key,
        )
        response = requests.post(
            url,
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        # Parse top prediction
        predictions = data.get("predictions", [])
        if not predictions:
            logger.warning("Roboflow returned empty predictions: %s", data)
            return None

        top = max(predictions, key=lambda p: p.get("confidence", 0))
        class_name = top.get("class", "rock").lower()
        confidence = float(top.get("confidence", 0.0))
        meta = _CLASS_META.get(class_name, _CLASS_META["rock"])

        # Build all_predictions list
        all_preds = [
            {
                "class": p.get("class", ""),
                "confidence": round(float(p.get("confidence", 0)) * 100, 1),
            }
            for p in sorted(predictions, key=lambda p: p.get("confidence", 0), reverse=True)
        ]

        return {
            "name": meta["full_name"],
            "chemical_formula": meta["formula"],
            "category": meta["category"],
            "commercial_value": meta["commercial_value"],
            "confidence": round(confidence * 100, 1),
            "purity_percentage": round(confidence * 100, 1),
            "roboflow_class": class_name,
            "all_predictions": all_preds,
            "source": "roboflow",
            "primary_elements": [],
            "associated_minerals": [],
            "industrial_uses": [],
            "description": (
                f"Classified as {meta['full_name']} ({meta['formula']}) "
                f"with {round(confidence * 100, 1)}% confidence by the Roboflow ore_dataset model."
            ),
        }

    except Exception as exc:
        logger.error("Roboflow inference failed: %s", exc)
        return None


def get_dataset_info() -> dict[str, Any]:
    """Return metadata about the ore_dataset project."""
    return {
        "workspace": Config.ROBOFLOW_WORKSPACE,
        "project": Config.ROBOFLOW_PROJECT,
        "version": Config.ROBOFLOW_VERSION,
        "classes": list(_CLASS_META.keys()),
        "class_count": len(_CLASS_META),
        "dataset_url": "https://universe.roboflow.com/mineral1/ore_dataset",
    }
