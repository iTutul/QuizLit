"""pages/results.py — Results Review page (T023 + T024 + T025 + T034)."""
import datetime

import pandas as pd
import streamlit as st

from components.category_chart import render_category_chart, render_strength_weakness_charts
import logic.exporter as exporter

# ---------------------------------------------------------------------------
# Session guard (T023)
# ---------------------------------------------------------------------------
if not st.session_state.get("session_submitted"):
    st.switch_page("pages/setup.py")
    st.stop()

results = st.session_state.results

# ---------------------------------------------------------------------------
# T023: Header, score, and verdict
# ---------------------------------------------------------------------------
st.title("Results")

col_meta1, col_meta2 = st.columns(2)
with col_meta1:
    st.write(f"**Name:** {results['user_name']}")
with col_meta2:
    st.write(f"**Date:** {datetime.date.today().isoformat()}")

st.divider()

col_score, col_verdict = st.columns([1, 2])
with col_score:
    st.metric(
        label="Total Score",
        value=f"{results['total_score']} / {results['max_score']}",
    )
with col_verdict:
    if results["passed"]:
        st.success("✅ PASS")
    else:
        st.error("❌ FAIL")
    st.caption(f"Pass mark: {results['pass_mark']}/{results['max_score']} (60%)")

st.divider()

# ---------------------------------------------------------------------------
# T024: Per-question review
# ---------------------------------------------------------------------------
st.header("Question Review")

# Build option-text lookup from the drawn questions still in session state
q_lookup = {q["id"]: q for q in st.session_state.questions}

for i, pq in enumerate(results["per_question"]):
    expander_label = f"Question {i + 1} — {pq['primary_category']}"
    with st.expander(expander_label, expanded=False):
        # Scenario
        if pq["scenario"]:
            st.info(pq["scenario"])

        # Question text
        st.write(pq["question"])
        st.write("")

        if pq["selected_option_id"] is not None:
            # Answered question
            selected_id = pq["selected_option_id"]
            st.metric("Points earned", pq["points_earned"])

            # Options table: all 4 options with points and selection marker
            orig_options = q_lookup[pq["question_id"]]["options"]
            rows = []
            for opt_id in ["A", "B", "C", "D"]:
                rows.append(
                    {
                        "Option": opt_id,
                        "Answer": orig_options[opt_id],
                        "Points": pq["points_lookup"][opt_id],
                        "Selected": "✓" if opt_id == selected_id else "",
                    }
                )
            options_df = pd.DataFrame(rows).set_index("Option")
            st.dataframe(options_df, use_container_width=True)

            # Rationale for all 4 options
            st.subheader("Rationale")
            for opt_id in ["A", "B", "C", "D"]:
                tier = pq["tier_for_option"][opt_id]
                rationale_key = f"why_{tier}"
                rationale_text = pq["rationale"][rationale_key]
                pts = pq["points_lookup"][opt_id]
                marker = " ← **your answer**" if opt_id == selected_id else ""
                st.markdown(
                    f"**Option {opt_id}** ({pts} pts){marker}: {rationale_text}"
                )

        else:
            # Unanswered question — no rationale shown per spec
            st.write("Not answered — 0 points")

st.divider()

# ---------------------------------------------------------------------------
# T025: Category breakdown chart + summary table
# ---------------------------------------------------------------------------
st.header("Category Breakdown")

render_category_chart(results["category_breakdown"])

if results["category_breakdown"]:
    table_rows = []
    for cat in sorted(results["category_breakdown"].keys()):
        data = results["category_breakdown"][cat]
        s_pct = (
            round(data["session_points"] / data["session_max"] * 100, 1)
            if data["session_max"] > 0
            else 0.0
        )
        c_pct = (
            round(data["cumulative_points"] / data["cumulative_max"] * 100, 1)
            if data["cumulative_max"] > 0
            else 0.0
        )
        table_rows.append(
            {
                "Category": cat,
                "Session Pts / Max": f"{data['session_points']} / {data['session_max']}",
                "Session %": s_pct,
                "Cumulative Pts / Max": (
                    f"{data['cumulative_points']} / {data['cumulative_max']}"
                ),
                "Cumulative %": c_pct,
            }
        )
    st.dataframe(
        pd.DataFrame(table_rows).set_index("Category"),
        use_container_width=True,
    )

if results["category_breakdown"]:
    st.subheader("Strengths & Weaknesses")
    st.caption("Based on cumulative scores across all sessions. Bigger slice = larger gap to perfect (weaknesses) or stronger performance (strengths). Up to 10 categories shown per chart.")
    render_strength_weakness_charts(results["category_breakdown"])

st.divider()

# ---------------------------------------------------------------------------
# T025: Start New Session button — clears all quiz state
# ---------------------------------------------------------------------------
_KEYS_TO_CLEAR = [
    "session_active",
    "session_submitted",
    "questions",
    "shuffled_options",
    "shuffle_maps",
    "points_lookups",
    "answers",
    "flags",
    "current_question_idx",
    "start_time",
    "time_extension_used",
    "results",
    "historical_scorecard",
]

# ---------------------------------------------------------------------------
# T034: Scorecard download
# ---------------------------------------------------------------------------
st.subheader("Download Scorecard")
try:
    scorecard_bytes = exporter.build_scorecard(
        results, st.session_state.get("historical_scorecard")
    )
    st.download_button(
        label="📥 Download Scorecard (.xlsx)",
        data=scorecard_bytes,
        file_name=f"togaf_scorecard_{datetime.date.today().isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
except Exception as e:
    st.error(f"Export failed: {e}")

st.divider()

if st.button("▶ Start New Session", type="primary", use_container_width=True):
    # Snapshot cumulative scores so the next session carries them forward automatically
    if results.get("category_breakdown"):
        st.session_state._persistent_scorecard = {
            "category_summary": {
                cat: {
                    "cumulative_points": data["cumulative_points"],
                    "cumulative_max": data["cumulative_max"],
                }
                for cat, data in results["category_breakdown"].items()
            }
        }
    for key in _KEYS_TO_CLEAR:
        st.session_state.pop(key, None)
    st.switch_page("pages/setup.py")
