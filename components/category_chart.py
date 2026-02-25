"""components/category_chart.py — Category performance charts (T022)."""
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def render_category_chart(category_breakdown: dict) -> None:
    """
    Render a horizontal grouped bar chart of session vs cumulative performance.

    Args:
        category_breakdown: dict mapping category name →
            {session_points, session_max, cumulative_points, cumulative_max}

    Shows:
        - Blue bars: session percentage (session_points / session_max × 100)
        - Green bars: cumulative percentage (cumulative_points / cumulative_max × 100)
        - Red dashed vertical line at x=60 (60% pass mark)

    If the breakdown dict is empty, renders an info message instead.
    """
    if not category_breakdown:
        st.info("No category data available.")
        return

    categories = sorted(category_breakdown.keys())
    session_pcts = []
    cumulative_pcts = []
    for cat in categories:
        data = category_breakdown[cat]
        s_pct = (
            data["session_points"] / data["session_max"] * 100
            if data["session_max"] > 0
            else 0.0
        )
        c_pct = (
            data["cumulative_points"] / data["cumulative_max"] * 100
            if data["cumulative_max"] > 0
            else 0.0
        )
        session_pcts.append(round(s_pct, 1))
        cumulative_pcts.append(round(c_pct, 1))

    n = len(categories)
    bar_h = 0.35
    y = np.arange(n)

    fig, ax = plt.subplots(figsize=(10, max(4, n * 0.7)))

    ax.barh(y + bar_h / 2, session_pcts, bar_h, label="This Session", color="steelblue")
    ax.barh(y - bar_h / 2, cumulative_pcts, bar_h, label="Cumulative", color="mediumseagreen")

    ax.axvline(x=60, color="red", linestyle="--", linewidth=1.5, label="Pass mark (60%)")

    ax.set_yticks(y)
    ax.set_yticklabels(categories, fontsize=9)
    ax.set_xlabel("Score (%)")
    ax.set_xlim(0, 105)
    ax.set_title("Category Performance")
    ax.legend(loc="lower right")
    fig.tight_layout()

    st.pyplot(fig, clear_figure=True)


def render_strength_weakness_charts(category_breakdown: dict) -> None:
    """
    Render two side-by-side pie charts based on cumulative category scores.

    Left  — Weaknesses: up to 10 lowest-scoring categories.
             Slice size proportional to the gap from 100 % (bigger slice = bigger gap).
    Right — Strengths:  up to 10 highest-scoring categories.
             Slice size proportional to the cumulative score % (bigger slice = stronger).

    Uses cumulative scores so results compound across sessions.
    """
    if not category_breakdown:
        return

    def _pct(data: dict) -> float:
        return (
            round(data["cumulative_points"] / data["cumulative_max"] * 100, 1)
            if data["cumulative_max"] > 0
            else 0.0
        )

    def _truncate(name: str, n: int = 30) -> str:
        return name if len(name) <= n else name[:n] + "…"

    scored = sorted(
        ((cat, _pct(data)) for cat, data in category_breakdown.items()),
        key=lambda x: x[1],
    )

    weak_10 = scored[:10]           # lowest first
    strong_10 = scored[-10:][::-1]  # highest first

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Weaknesses ---
    weak_sizes = [max(100 - pct, 0.5) for _, pct in weak_10]
    weak_labels = [f"{_truncate(cat)} ({pct}%)" for cat, pct in weak_10]
    colors_red = plt.cm.Reds(np.linspace(0.85, 0.35, len(weak_10)))
    wedges1, _ = ax1.pie(
        weak_sizes,
        startangle=90,
        colors=colors_red,
        wedgeprops={"edgecolor": "white", "linewidth": 0.8},
    )
    ax1.set_title("Weaknesses", fontsize=13, fontweight="bold", pad=14)
    ax1.legend(
        wedges1,
        weak_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.38),
        fontsize=7.5,
        frameon=False,
    )

    # --- Strengths ---
    strong_sizes = [max(pct, 0.5) for _, pct in strong_10]
    strong_labels = [f"{_truncate(cat)} ({pct}%)" for cat, pct in strong_10]
    colors_green = plt.cm.Greens(np.linspace(0.85, 0.35, len(strong_10)))
    wedges2, _ = ax2.pie(
        strong_sizes,
        startangle=90,
        colors=colors_green,
        wedgeprops={"edgecolor": "white", "linewidth": 0.8},
    )
    ax2.set_title("Strengths", fontsize=13, fontweight="bold", pad=14)
    ax2.legend(
        wedges2,
        strong_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.38),
        fontsize=7.5,
        frameon=False,
    )

    fig.subplots_adjust(bottom=0.28)
    st.pyplot(fig, clear_figure=True)
