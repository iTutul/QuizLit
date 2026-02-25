"""components/question_card.py — Question display widget (T019)."""
import streamlit as st


def render_question_card(
    question: dict,
    shuffled_options: list,
    answer: dict | None,
) -> None:
    """
    Render question scenario, stem, and answer radio for one question.

    Args:
        question:        Question dict from the question bank.
        shuffled_options: List of {option_id, text, display_idx} for this question.
        answer:          Current answer dict {display_idx, original_option_id, points}
                         or None if not yet answered.
    """
    if question.get("scenario"):
        st.info(question["scenario"])

    st.subheader(question["question"])

    option_texts = [opt["text"] for opt in shuffled_options]
    current_index = answer["display_idx"] if answer else None
    q_key = f"q_{question['id']}"

    st.radio(
        label=" ",
        options=option_texts,
        index=current_index,
        key=q_key,
    )
