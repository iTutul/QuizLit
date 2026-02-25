import random


def shuffle_questions(questions: list, seed=None) -> list:
    """Return a new list of questions in randomized order. Input is not mutated."""
    return random.Random(seed).sample(questions, len(questions))


def shuffle_options(question: dict, seed=None) -> tuple:
    """
    Shuffle a question's options for display.

    Returns:
        (shuffled_options, shuffle_map) where:
        - shuffled_options: list of 4 dicts {option_id, text, display_idx}
        - shuffle_map: {display_idx (int) → original_option_id (str)}
    Input question dict is not mutated.
    """
    pairs = list(question["options"].items())  # [("A", "text"), ...]
    rng = random.Random(seed)
    rng.shuffle(pairs)
    shuffled_options = [
        {"option_id": oid, "text": text, "display_idx": i}
        for i, (oid, text) in enumerate(pairs)
    ]
    shuffle_map = {i: oid for i, (oid, _) in enumerate(pairs)}
    return shuffled_options, shuffle_map
