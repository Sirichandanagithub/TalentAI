from typing import Any


def clamp_score(score: float) -> float:
    """
    Keep a score within the valid 0-100 range.
    """
    return round(max(0.0, min(100.0, float(score))), 2)


def calculate_percentage(
    obtained: float,
    total: float
) -> float:
    """
    Convert obtained marks into a percentage.
    """
    if total <= 0:
        return 0.0

    return clamp_score((obtained / total) * 100)


def weighted_score(
    components: dict[str, float],
    weights: dict[str, float]
) -> float:
    """
    Calculate a weighted score.

    Only components supplied with valid numeric scores
    are included. Their weights are normalized.
    """
    weighted_total = 0.0
    available_weight = 0.0

    for component, weight in weights.items():
        score = components.get(component)

        if score is None:
            continue

        if not isinstance(score, (int, float)):
            continue

        if weight < 0:
            raise ValueError("Weights cannot be negative.")

        weighted_total += clamp_score(score) * weight
        available_weight += weight

    if available_weight == 0:
        return 0.0

    return clamp_score(weighted_total / available_weight)


def classify_score(score: float) -> str:
    """
    Classify a score into a readable performance level.
    """
    score = clamp_score(score)

    if score >= 85:
        return "excellent"
    elif score >= 70:
        return "strong"
    elif score >= 55:
        return "moderate"
    elif score >= 40:
        return "needs_improvement"
    else:
        return "poor"


def safe_list(value: Any) -> list:
    """
    Safely convert supported values into a list.
    """
    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if value is None:
        return []

    return [value]


def safe_dict(value: Any) -> dict:
    """
    Return a dictionary only when the input is a dictionary.
    """
    return value if isinstance(value, dict) else {}


def normalize_text(value: Any) -> str:
    """
    Normalize text for consistent comparisons.
    """
    if value is None:
        return ""

    return " ".join(str(value).strip().lower().split())