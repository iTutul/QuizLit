import pandas as pd


def load_tags(file_obj) -> dict:
    """Load togaf_tags_db.csv and return {tag_id (int): {"name": ..., "category": ...}}."""
    df = pd.read_csv(file_obj)
    required = {"tag_id", "tag_name", "tag_category"}
    missing = required - set(df.columns)
    if missing:
        # Report each missing column individually for clear error messages
        for col in sorted(missing):
            raise ValueError(f"Missing required column: '{col}'")
    return {
        int(row.tag_id): {"name": row.tag_name, "category": row.tag_category}
        for row in df.itertuples()
    }


def get_tag_names_for_question(question: dict, tag_map: dict) -> list:
    """Resolve a question's integer tag_ids to tag_name strings (deduped, ordered)."""
    seen = set()
    result = []
    for tag_id in question.get("tags", []):
        if tag_id in tag_map:
            name = tag_map[tag_id]["name"]
            if name not in seen:
                seen.add(name)
                result.append(name)
    return result


def get_all_tag_names(questions: list, tag_map: dict) -> list:
    """Return sorted unique tag_names present across all questions."""
    return sorted(
        {name for q in questions for name in get_tag_names_for_question(q, tag_map)}
    )


def get_tag_id_for_name(tag_name: str, tag_map: dict):
    """Return the integer tag_id for a given tag_name, or None if not found."""
    for tag_id, info in tag_map.items():
        if info["name"] == tag_name:
            return tag_id
    return None
