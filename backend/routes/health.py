"""Health check route."""

from flask import Blueprint, jsonify

from backend.config import Config

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health")
def health():
    """Return API health status."""
    return jsonify({
        "status": "ok",
        "gemini_model": Config.GEMINI_PRO_MODEL,
        "flash_model": Config.GEMINI_FLASH_MODEL,
        "api_key_configured": bool(Config.GEMINI_API_KEY),
    })
