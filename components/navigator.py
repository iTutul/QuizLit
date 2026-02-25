"""components/navigator.py — Question navigation sidebar widget (T018)."""
import streamlit as st


def render_navigator(
    questions: list,
    answers: dict,
    flags: set,
    current_idx: int,
) -> int | None:
    """
    Render question navigation buttons in the sidebar.

    Button label precedence (highest to lowest):
        1. current  → "▶ Q{n}"
        2. flagged  → "🚩 Q{n}"
        3. answered → "✓ Q{n}"
        4. unanswered → "○ Q{n}"

    Returns the 0-based index of the clicked button, or None if no click this
    render cycle. Does not mutate any state.
    """
    clicked = None
    for i, q in enumerate(questions):
        q_id = q["id"]
        if i == current_idx:
            label = f"▶ Q{i + 1}"
        elif q_id in flags:
            label = f"🚩 Q{i + 1}"
        elif q_id in answers:
            label = f"✓ Q{i + 1}"
        else:
            label = f"○ Q{i + 1}"

        if st.sidebar.button(label, key=f"nav_{i}", use_container_width=True):
            clicked = i

    return clicked
