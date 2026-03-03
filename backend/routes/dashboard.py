"""Dashboard route — GET /api/dashboard/stats."""

from collections import Counter

from flask import Blueprint, jsonify, session

from backend import dataset_manager
from backend.grading_engine import GRADE_COLORS, GRADE_LABELS

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/stats")
def stats():
    """Return aggregated stats for the analytics dashboard."""
    data = dataset_manager.get_stats()

    # Attach grade metadata for frontend
    data["grade_colors"] = GRADE_COLORS
    data["grade_labels"] = GRADE_LABELS

    # Session-based recent analyses (populated by /api/classify calls)
    recent = session.get("analyses_history", [])
    data["recent_analyses"] = recent[-10:]  # last 10

    # Ore class distribution (from Roboflow roboflow_class field)
    ore_class_counts = Counter(
        r.get("roboflow_class") or r.get("name", "unknown")
        for r in recent
    )
    data["ore_class_distribution"] = dict(ore_class_counts)

    # Classifier source distribution
    source_counts = Counter(
        r.get("classifier_source", "unknown") for r in recent
    )
    data["classifier_source_distribution"] = dict(source_counts)

    # Integrated dataset sources
    data["dataset_sources"] = [
        {
            "name": "Roboflow ore_dataset",
            "description": "6-class ore image classification dataset",
            "url": "https://universe.roboflow.com/",
            "classes": ["hematite", "magnetite", "limonite", "pyrite", "ilmenite", "quartz"],
        },
        {
            "name": "Mineral Photos Dataset",
            "description": "Kaggle reference photos by Florian Geillon",
            "url": "https://www.kaggle.com/datasets/floriangeillon/mineral-photos",
            "license": "CC BY 4.0",
        },
        {
            "name": "Rock Classification Dataset",
            "description": "Kaggle rock images by Salman Eunus",
            "url": "https://www.kaggle.com/datasets/salmaneunus/rock-classification",
            "license": "CC BY-SA 4.0",
        },
    ]

    return jsonify(data)
