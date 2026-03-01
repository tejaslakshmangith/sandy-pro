"""Quality grading engine for rock/mineral/ore classification."""

GRADE_THRESHOLDS = {
    "A1": (95, 100),
    "A2": (85, 94.99),
    "A3": (75, 84.99),
    "B1": (65, 74.99),
    "B2": (55, 64.99),
    "B3": (45, 54.99),
    "C1": (30, 44.99),
    "C2": (0, 29.99),
}

GRADE_COLORS = {
    "A1": "#00ff88",
    "A2": "#44ff66",
    "A3": "#88ff44",
    "B1": "#ffcc00",
    "B2": "#ff8800",
    "B3": "#ff4400",
    "C1": "#cc2200",
    "C2": "#880000",
}

GRADE_LABELS = {
    "A1": "Premium Export Quality",
    "A2": "High Commercial Grade",
    "A3": "Standard Industrial Grade",
    "B1": "Low Industrial Grade",
    "B2": "Processing Required",
    "B3": "Heavy Processing Needed",
    "C1": "Marginal Viability",
    "C2": "Waste/Gangue Material",
}


def compute_grade(purity_percentage: float) -> dict:
    """Compute quality grade from purity percentage.

    Args:
        purity_percentage: Float between 0 and 100.

    Returns:
        Dict with grade, color, label, and purity.
    """
    purity = max(0.0, min(100.0, float(purity_percentage)))

    grade = "C2"
    for g, (low, high) in GRADE_THRESHOLDS.items():
        if low <= purity <= high:
            grade = g
            break

    return {
        "grade": grade,
        "color": GRADE_COLORS[grade],
        "label": GRADE_LABELS[grade],
        "purity": purity,
    }


def get_grade_info(grade: str) -> dict:
    """Return color and label for a given grade code."""
    grade = grade.upper()
    return {
        "grade": grade,
        "color": GRADE_COLORS.get(grade, "#888888"),
        "label": GRADE_LABELS.get(grade, "Unknown"),
    }
