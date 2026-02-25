from data.tag_resolver import get_tag_names_for_question

# TOGAF 10 Practitioner: 60% of 40 points required to pass.
PASS_MARK: int = 24


def build_points_lookup(scoring: dict) -> dict:
    """Convert hierarchical scoring block to flat {option_id: points}."""
    return {tier["option"]: tier["points"] for tier in scoring.values()}


def resolve_score(points_lookup: dict, shuffle_map: dict, selected_display_idx: int) -> int:
    """Return points for a selected display index via the shuffle map."""
    return points_lookup[shuffle_map[selected_display_idx]]


def build_tier_lookup(scoring: dict) -> dict:
    """Return {option_id: tier_name} inverse map from a scoring block."""
    return {tier["option"]: tier_name for tier_name, tier in scoring.items()}


def score_session(
    questions: list,
    points_lookups: dict,
    shuffle_maps: dict,
    answers: dict,
) -> int:
    """Sum points across all answered questions; unanswered questions score 0."""
    total = 0
    for q in questions:
        q_id = q["id"]
        if q_id in answers:
            total += answers[q_id]["points"]
    return total


def compute_category_breakdown(
    questions: list,
    points_lookups: dict,
    shuffle_maps: dict,
    answers: dict,
    tag_map: dict,
) -> dict:
    """
    Return {tag_name: {session_points, session_max}} for every tag present in questions.
    Questions with multiple tags contribute to all their categories.
    Unanswered questions contribute 0 to session_points and 5 to session_max.
    """
    breakdown = {}
    for q in questions:
        q_id = q["id"]
        tag_names = get_tag_names_for_question(q, tag_map)
        points = answers[q_id]["points"] if q_id in answers else 0
        for name in tag_names:
            if name not in breakdown:
                breakdown[name] = {"session_points": 0, "session_max": 0}
            breakdown[name]["session_points"] += points
            breakdown[name]["session_max"] += 5
    return breakdown


def merge_historical(breakdown: dict, historical_scorecard) -> dict:
    """
    Merge session breakdown with optional historical scorecard data.

    If historical_scorecard is None, cumulative == session values.
    Categories present only in historical appear with session_points=0, session_max=0.
    """
    result = {}
    for category, data in breakdown.items():
        cumulative_points = data["session_points"]
        cumulative_max = data["session_max"]
        if historical_scorecard is not None:
            hist = (
                historical_scorecard.get("category_summary", {}).get(category, {})
            )
            cumulative_points += hist.get("cumulative_points", 0)
            cumulative_max += hist.get("cumulative_max", 0)
        result[category] = {
            "session_points": data["session_points"],
            "session_max": data["session_max"],
            "cumulative_points": cumulative_points,
            "cumulative_max": cumulative_max,
        }

    # Include historical-only categories
    if historical_scorecard is not None:
        for category, hist in historical_scorecard.get("category_summary", {}).items():
            if category not in result:
                result[category] = {
                    "session_points": 0,
                    "session_max": 0,
                    "cumulative_points": hist.get("cumulative_points", 0),
                    "cumulative_max": hist.get("cumulative_max", 0),
                }

    return result


def is_passing(total_score: int, pass_mark: int = PASS_MARK) -> bool:
    """Return True if total_score meets or exceeds pass_mark."""
    return total_score >= pass_mark
