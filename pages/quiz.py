"""pages/quiz.py — Exam Mode Session orchestrator (T020 + T021)."""
import time

import streamlit as st

import data.tag_resolver as tag_resolver
import logic.scoring as scoring
from components.navigator import render_navigator
from components.question_card import render_question_card
from components.timer import render_timer

# ---------------------------------------------------------------------------
# Session guards
# ---------------------------------------------------------------------------
if not st.session_state.get("session_active"):
    st.switch_page("pages/setup.py")
    st.stop()

if st.session_state.get("session_submitted"):
    st.switch_page("pages/results.py")
    st.stop()

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Pull frequently accessed state into local vars (read-only references)
# ---------------------------------------------------------------------------
questions = st.session_state.questions
shuffled_options = st.session_state.shuffled_options
shuffle_maps = st.session_state.shuffle_maps
points_lookups = st.session_state.points_lookups
time_limit_seconds = st.session_state.time_limit_seconds
tag_map = st.session_state.tag_map

current_idx = st.session_state.current_question_idx
current_q = questions[current_idx]
q_id = current_q["id"]
opts = shuffled_options[q_id]


# ---------------------------------------------------------------------------
# T021: _submit_session() — compute scores and store results
# ---------------------------------------------------------------------------
def _submit_session() -> None:
    """Finalise the session: compute all scores and store results in session state."""
    qs = st.session_state.questions
    pl = st.session_state.points_lookups
    sm = st.session_state.shuffle_maps
    ans = st.session_state.answers
    tm = st.session_state.tag_map

    total_score = scoring.score_session(qs, pl, sm, ans)
    passed = scoring.is_passing(total_score)
    breakdown = scoring.compute_category_breakdown(qs, pl, sm, ans, tm)
    category_breakdown = scoring.merge_historical(
        breakdown, st.session_state.get("historical_scorecard")
    )

    per_question = []
    for q in qs:
        qid = q["id"]
        tier_lookup = scoring.build_tier_lookup(q["scoring"])
        tag_names = tag_resolver.get_tag_names_for_question(q, tm)
        per_question.append(
            {
                "question_id": qid,
                "scenario": q["scenario"],
                "question": q["question"],
                "selected_option_id": ans[qid]["original_option_id"] if qid in ans else None,
                "points_earned": ans[qid]["points"] if qid in ans else 0,
                "points_lookup": pl[qid],
                "tier_for_option": tier_lookup,
                "rationale": q["rationale"],
                "tag_names": tag_names,
                "primary_category": tag_names[0] if tag_names else "",
            }
        )

    st.session_state.results = {
        "total_score": total_score,
        "max_score": 40,
        "pass_mark": scoring.PASS_MARK,
        "passed": passed,
        "per_question": per_question,
        "category_breakdown": category_breakdown,
        "user_name": st.session_state.user_name,
    }
    st.session_state.session_submitted = True
    st.session_state.session_active = False


# ---------------------------------------------------------------------------
# (1) Commit current radio value at the top of every render
#
# st.session_state[f"q_{q_id}"] holds the selected option TEXT for the current
# question (set by Streamlit's widget key mechanism from the previous render).
# We read it here — before any widgets are rendered — so the selection is
# captured even if the timer fires and triggers submission before the question
# card below gets a chance to render.
# ---------------------------------------------------------------------------
selected_text = st.session_state.get(f"q_{q_id}")
if selected_text is not None:
    for opt in opts:
        if opt["text"] == selected_text:
            new_answer = {
                "display_idx": opt["display_idx"],
                "original_option_id": opt["option_id"],
                "points": points_lookups[q_id][opt["option_id"]],
            }
            if st.session_state.answers.get(q_id) != new_answer:
                st.session_state.answers[q_id] = new_answer
            break

# ---------------------------------------------------------------------------
# Sidebar — layout order: timer, then navigator, then submit
# ---------------------------------------------------------------------------
# st.sidebar.title(f"Good luck, {st.session_state.user_name}!")

# (2) Timer — auto-submit on expiry
timer_expired = render_timer(st.session_state.start_time, time_limit_seconds)
if timer_expired:
    _submit_session()
    st.switch_page("pages/results.py")
    st.stop()

# (3) Navigator
st.sidebar.subheader("Questions")
nav_click = render_navigator(
    questions,
    st.session_state.answers,
    st.session_state.flags,
    current_idx,
)
if nav_click is not None and nav_click != current_idx:
    st.session_state.current_question_idx = nav_click
    st.rerun()

st.sidebar.divider()

# Submit button
answered_count = len(st.session_state.answers)
st.sidebar.caption(f"Answered: {answered_count} / {len(questions)}")
if st.sidebar.button(
    "Submit Session",
    type="primary",
    use_container_width=True,
    key="submit_btn",
):
    _submit_session()
    st.switch_page("pages/results.py")
    st.stop()

# ---------------------------------------------------------------------------
# Main content area
# ---------------------------------------------------------------------------
main = st.container()

with main:
    st.title(f"Question {current_idx + 1} of {len(questions)}")

    # (4) Flag toggle
    is_flagged = q_id in st.session_state.flags
    flag_label = "🚩 Unflag Question" if is_flagged else "🚩 Flag for Review"
    if st.button(flag_label, key="flag_btn"):
        if is_flagged:
            st.session_state.flags.discard(q_id)
        else:
            st.session_state.flags.add(q_id)
        st.rerun()

    st.divider()

    # (5) Question card
    render_question_card(
        current_q,
        opts,
        st.session_state.answers.get(q_id),
    )

    # (6) Previous / Next / Submit navigation buttons
    st.divider()
    is_last = current_idx == len(questions) - 1
    prev_col, next_col = st.columns(2)
    with prev_col:
        prev_clicked = st.button("← Previous", disabled=current_idx == 0, use_container_width=True, key="prev_btn")
    with next_col:
        if is_last:
            inline_submit = st.button("Submit Session", type="primary", use_container_width=True, key="inline_submit_btn")
        else:
            next_clicked = st.button("Next →", use_container_width=True, key="next_btn")

if prev_clicked:
    st.session_state.current_question_idx = current_idx - 1
    st.rerun()
if not is_last and next_clicked:
    st.session_state.current_question_idx = current_idx + 1
    st.rerun()
if is_last and inline_submit:
    _submit_session()
    st.switch_page("pages/results.py")
    st.stop()

# ---------------------------------------------------------------------------
# Timer tick
# ---------------------------------------------------------------------------
time.sleep(1)
st.rerun()

# ---------------------------------------------------------------------------
# CONSTITUTION AUDIT (T041)
# Principle 1 — Streamlit-free logic layer:
#   logic/ and data/ modules imported above contain NO "import streamlit"
#   statements. Verified by grep in Phase 8 (exit code 1 = no matches).
# Principle 2 — Deterministic scoring invariant:
#   Answers committed at top of render (before any widget) ensure
#   score_session() always operates on the latest user selection,
#   even when timer fires mid-render.
# Principle 3 — Answers committed before navigation:
#   st.session_state.answers[q_id] is written at the top of this page
#   before any call to st.switch_page() or st.rerun().
# Principle 4 — Pass mark single source of truth:
#   scoring.PASS_MARK = 24 is defined once in logic/scoring.py.
#   Both this page and logic/exporter.py reference that constant.
# ---------------------------------------------------------------------------
