"""Dataset route — GET /api/dataset."""

import csv
import io
import json
import pathlib

from flask import Blueprint, jsonify, request, Response

from backend import dataset_manager

dataset_bp = Blueprint("dataset", __name__)


@dataset_bp.route("/api/dataset")
def get_dataset():
    """Return paginated, filtered dataset records."""
    result = dataset_manager.get_all(
        search=request.args.get("search", ""),
        category=request.args.get("category", ""),
        grade=request.args.get("grade", ""),
        formation_type=request.args.get("formation_type", ""),
        commercial_value=request.args.get("commercial_value", ""),
        sort_by=request.args.get("sort_by", "name"),
        sort_order=request.args.get("sort_order", "asc"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 20)),
    )
    return jsonify(result)


@dataset_bp.route("/api/dataset/export")
def export_csv():
    """Export full dataset as CSV."""
    records = dataset_manager.get_all_records()
    if not records:
        return jsonify({"error": "No data"}), 404

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=minerals_dataset.csv"},
    )


@dataset_bp.route("/api/dataset/<int:row_id>")
def get_row(row_id: int):
    """Return a single dataset row by id."""
    row = dataset_manager.get_row(row_id)
    if row is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(row)


@dataset_bp.route("/api/dataset/minerals-meta")
def minerals_meta():
    """Return Kaggle minerals reference metadata."""
    path = pathlib.Path("data/kaggle_minerals_meta.json")
    if not path.exists():
        return jsonify({"error": "Not found"}), 404
    return jsonify(json.loads(path.read_text()))
