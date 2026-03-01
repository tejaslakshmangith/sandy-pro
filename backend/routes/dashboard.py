"""Dashboard route — GET /api/dashboard/stats."""

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

    return jsonify(data)
