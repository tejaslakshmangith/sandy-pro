"""Roboflow dataset info route — GET /api/roboflow/info."""

from flask import Blueprint, jsonify
from backend.roboflow_service import get_dataset_info
from backend.config import Config

roboflow_bp = Blueprint("roboflow", __name__)


@roboflow_bp.route("/api/roboflow/info")
def roboflow_info():
    """Return ore_dataset metadata and API key status."""
    info = get_dataset_info()
    info["api_key_configured"] = bool(Config.ROBOFLOW_API_KEY)
    return jsonify(info)
