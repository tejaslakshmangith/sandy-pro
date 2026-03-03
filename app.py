"""Sandy Pro — Flask Application Entry Point."""

import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS

from backend.config import Config


def create_app():
    """Application factory pattern."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register blueprints
    from backend.routes.health import health_bp
    from backend.routes.classify import classify_bp
    from backend.routes.dataset import dataset_bp
    from backend.routes.dashboard import dashboard_bp
    from backend.routes.roboflow_info import roboflow_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(classify_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(roboflow_bp)

    # Page routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/result")
    def result():
        return render_template("result.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/dataset")
    def dataset():
        return render_template("dataset.html")

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "status": 404}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error", "status": 500}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
