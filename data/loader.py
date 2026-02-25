import json
import random

_REQUIRED_RATIONALE_KEYS = {
    "why_best",
    "why_second_best",
    "why_third_best",
    "why_distractor",
    "concept_tested",
    "common_mistakes",
    "togaf_reference",
}
_REQUIRED_TIER_KEYS = {"best", "second_best", "third_best", "distractor"}
_VALID_OPTION_IDS = {"A", "B", "C", "D"}
_VALID_POINTS = {5, 3, 1, 0}


def load_question_bank(file_obj) -> list:
    """Load and validate a JSON question bank from a file-like object."""
    data = json.load(file_obj)
    if not isinstance(data, list):
        raise ValueError("Question bank must be a JSON array")

    questions = []
    seen_ids = set()

    for q in data:
        q_id = q.get("id")
        if not isinstance(q_id, int):
            raise ValueError(f"Question {q_id}: field 'id' must be an integer")
        if q_id in seen_ids:
            raise ValueError(f"Question {q_id}: duplicate id")
        seen_ids.add(q_id)

        if "scenario" not in q or not isinstance(q["scenario"], str):
            raise ValueError(f"Question {q_id}: field 'scenario' must be a string")

        if "question" not in q:
            raise ValueError(f"Question {q_id}: field 'question' is missing")
        if not isinstance(q["question"], str) or not q["question"]:
            raise ValueError(f"Question {q_id}: field 'question' must be a non-empty string")

        options = q.get("options", {})
        if not isinstance(options, dict) or set(options.keys()) != _VALID_OPTION_IDS:
            raise ValueError(
                f"Question {q_id}: field 'options' must have exactly 4 keys A/B/C/D"
            )
        for key, val in options.items():
            if not isinstance(val, str) or not val:
                raise ValueError(
                    f"Question {q_id}: option '{key}' must be a non-empty string"
                )

        scoring = q.get("scoring", {})
        if not isinstance(scoring, dict) or set(scoring.keys()) != _REQUIRED_TIER_KEYS:
            raise ValueError(
                f"Question {q_id}: field 'scoring' must have exactly keys "
                f"{_REQUIRED_TIER_KEYS}"
            )
        option_vals = set()
        points_vals = set()
        for tier_name, tier in scoring.items():
            if "option" not in tier or "points" not in tier:
                raise ValueError(
                    f"Question {q_id}: scoring tier '{tier_name}' missing 'option' or 'points'"
                )
            option_vals.add(tier["option"])
            points_vals.add(tier["points"])
        if option_vals != _VALID_OPTION_IDS:
            raise ValueError(
                f"Question {q_id}: scoring option values must be exactly "
                f"{{'A','B','C','D'}}"
            )
        if points_vals != _VALID_POINTS:
            raise ValueError(
                f"Question {q_id}: scoring points must be exactly {{5,3,1,0}}"
            )

        tags = q.get("tags", [])
        if not isinstance(tags, list) or len(tags) == 0:
            raise ValueError(f"Question {q_id}: field 'tags' must be a non-empty list")

        rationale = q.get("rationale", {})
        if not isinstance(rationale, dict) or not _REQUIRED_RATIONALE_KEYS.issubset(
            set(rationale.keys())
        ):
            raise ValueError(
                f"Question {q_id}: field 'rationale' is missing required keys"
            )

        questions.append(q)

    return questions


def filter_by_tags(questions: list, tag_ids: list) -> list:
    """Return questions whose tags intersect tag_ids. Input list is not mutated."""
    tag_set = set(tag_ids)
    return [q for q in questions if set(q["tags"]) & tag_set]


def draw_session_questions(questions: list, n: int = 8) -> list:
    """Return a random sample of n questions. Raises ValueError if insufficient."""
    if len(questions) < n:
        raise ValueError(
            f"Need {n} questions but only {len(questions)} match the selected categories"
        )
    return random.sample(questions, n)
