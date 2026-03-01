"""Dataset manager — loads and queries the minerals CSV dataset."""

import logging
import os

import pandas as pd

from backend.config import Config

logger = logging.getLogger(__name__)

_df: pd.DataFrame | None = None


def _load() -> pd.DataFrame:
    """Load dataset from CSV, caching the result."""
    global _df
    if _df is not None:
        return _df

    path = Config.DATASET_PATH
    if not os.path.exists(path):
        logger.warning("Dataset not found at %s", path)
        _df = pd.DataFrame()
        return _df

    _df = pd.read_csv(path)
    logger.info("Dataset loaded: %d rows from %s", len(_df), path)
    return _df


def get_all(
    search: str = "",
    category: str = "",
    grade: str = "",
    formation_type: str = "",
    commercial_value: str = "",
    sort_by: str = "name",
    sort_order: str = "asc",
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """Return a paginated, filtered, sorted slice of the dataset.

    Returns:
        Dict with keys: data, total, page, per_page, pages.
    """
    df = _load().copy()

    if df.empty:
        return {"data": [], "total": 0, "page": page, "per_page": per_page, "pages": 0}

    # --- Filtering ---
    if search:
        mask = (
            df["name"].str.contains(search, case=False, na=False)
            | df["category"].str.contains(search, case=False, na=False)
            | df["chemical_formula"].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    if category:
        df = df[df["category"].str.lower() == category.lower()]

    if grade:
        df = df[df["quality_grade"].str.upper() == grade.upper()]

    if formation_type:
        df = df[df["formation_type"].str.lower() == formation_type.lower()]

    if commercial_value:
        df = df[df["commercial_value"].str.lower() == commercial_value.lower()]

    # --- Sorting ---
    sort_col_map = {
        "name": "name",
        "purity": "purity_percentage",
        "hardness": "hardness_mohs",
        "market_value": "market_value_usd_per_ton",
    }
    col = sort_col_map.get(sort_by, "name")
    if col in df.columns:
        ascending = sort_order.lower() != "desc"
        df = df.sort_values(col, ascending=ascending)

    # --- Pagination ---
    total = len(df)
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    start = (page - 1) * per_page
    end = start + per_page
    slice_df = df.iloc[start:end]

    return {
        "data": slice_df.fillna("").to_dict(orient="records"),
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


def get_stats() -> dict:
    """Return aggregate statistics for the dashboard."""
    df = _load()
    if df.empty:
        return {}

    stats: dict = {}

    # Category distribution
    stats["category_distribution"] = (
        df["category"].value_counts().to_dict()
    )

    # Grade distribution
    stats["grade_distribution"] = (
        df["quality_grade"].value_counts().to_dict()
    )

    # Formation type distribution
    stats["formation_distribution"] = (
        df["formation_type"].value_counts().to_dict()
    )

    # Commercial value breakdown
    stats["commercial_value_distribution"] = (
        df["commercial_value"].value_counts().to_dict()
    )

    # Average purity per category
    stats["avg_purity_by_category"] = (
        df.groupby("category")["purity_percentage"].mean().round(1).to_dict()
    )

    # Total rows
    stats["total_records"] = len(df)
    stats["avg_purity"] = round(df["purity_percentage"].mean(), 1)

    return stats


def get_row(row_id: int) -> dict | None:
    """Return a single row by id."""
    df = _load()
    if df.empty:
        return None
    rows = df[df["id"] == row_id]
    if rows.empty:
        return None
    return rows.iloc[0].fillna("").to_dict()


def get_all_records() -> list[dict]:
    """Return all records as a list of dicts (for CSV export)."""
    df = _load()
    if df.empty:
        return []
    return df.fillna("").to_dict(orient="records")
