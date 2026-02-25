"""components/timer.py — Countdown timer sidebar widget (T017)."""
import time

import streamlit as st


def render_timer(start_time: float, time_limit_seconds: int) -> bool:
    """
    Display countdown timer in the sidebar and handle the time extension button.
    Returns True if the time has expired, False otherwise.

    NOTE: The time.sleep(1) + st.rerun() tick cycle is owned by pages/quiz.py
    and placed at the END of each render, after all content has been drawn.
    This function does NOT call sleep or rerun internally (that would prevent
    the navigator and question card from rendering on each tick).
    """
    remaining = time_limit_seconds - (time.time() - start_time)

    if remaining <= 0:
        st.sidebar.error("⏰ Time's up!")
        return True

    minutes = int(remaining) // 60
    seconds = int(remaining) % 60
    st.sidebar.markdown(
        f"<h1 style='font-size:1.8rem; text-align:center; letter-spacing:0.05em;'>⏱ {minutes:02d}:{seconds:02d}</h1>",
        unsafe_allow_html=True,
    )

    if 0 < remaining <= 300 and not st.session_state.get("time_extension_used", False):
        if st.sidebar.button("⏱ Add 10 Minutes", key="time_extension_btn"):
            st.session_state.start_time -= 600
            st.session_state.time_extension_used = True
            st.rerun()

    return False
