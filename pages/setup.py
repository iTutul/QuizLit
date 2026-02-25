"""pages/setup.py — Session Setup & Launch (User Story 1)"""
import os
import time

import streamlit as st

import data.loader as loader
import data.tag_resolver as tag_resolver
import logic.importer as importer
import logic.shuffler as shuffler
import logic.scoring as scoring

# ---------------------------------------------------------------------------
# Session guards
# ---------------------------------------------------------------------------
if st.session_state.get("session_submitted"):
    st.switch_page("pages/results.py")
    st.stop()

if st.session_state.get("session_active"):
    st.switch_page("pages/quiz.py")
    st.stop()

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

title_ph = st.empty()

st.markdown("This is a application is to help you prepare for the TOGAF 10 Practitioner Exam. It is not affiliated with the TOGAF 10 Practitioner Exam or the Open Group.")
st.markdown("""
**What’s special about this**
1. Follows the actual question pattern — including the length of the scenarios and the answer options.
2. Every time you generate an exam, it shuffles the order of the questions.
3. It also shuffles the answer options for each question so you don’t end up memorizing them.
4. Free and unlimited usage
5. Upload your own question bank by using a JSON template file.
6. No registration or data collection.
""")
st.divider()

# ---------------------------------------------------------------------------
# Auto-load tag map on first page load
# ---------------------------------------------------------------------------
if "tag_map" not in st.session_state:
    try:
        with open("togaf_tags_db.csv", "rb") as _f:
            st.session_state.tag_map = tag_resolver.load_tags(_f)
    except Exception as e:
        st.error(f"Failed to load tag reference: {e}")
        st.stop()


# ---------------------------------------------------------------------------
# T014: Name
# ---------------------------------------------------------------------------
st.subheader("Your name")
user_name = st.text_input("Your name", placeholder="Enter your name", value=st.session_state.get("user_name", ""))

st.info('You can save your session results by downloading the scorecard.xlsx file at the end of the session.', icon="ℹ️")

title_ph.title(f"Hey {user_name.strip()}!" if user_name.strip() else "TOGAF 10 Practitioner Exam Simulator")


st.divider()

col1, col2 = st.columns(2, gap="large")

with col1:
    # ---------------------------------------------------------------------------
    # T014 + T015: Question Bank section
    # ---------------------------------------------------------------------------
    st.subheader("Question Bank")

    bank_files = sorted(f for f in os.listdir("bank") if f.endswith(".json"))
    selected_bank = bank_files[0] if bank_files else None

    uploaded_bank = None  # hidden — uncomment below to re-enable
    # uploaded_bank = st.file_uploader(
    #     "Or upload a custom question bank (.json)",
    #     type=["json"],
    #     key="bank_upload",
    # )

    # Determine current bank source key (uploaded file takes precedence)
    if uploaded_bank is not None:
        bank_source_key = f"upload:{uploaded_bank.name}:{uploaded_bank.size}"
    elif selected_bank is not None:
        bank_source_key = f"select:{selected_bank}"
    else:
        bank_source_key = None

    prev_bank_source_key = st.session_state.get("_bank_source_key")

    # Reload when bank source changes (includes the very first page load)
    if bank_source_key is not None and bank_source_key != prev_bank_source_key:
        try:
            if uploaded_bank is not None:
                questions = loader.load_question_bank(uploaded_bank)
            else:
                with open(os.path.join("bank", selected_bank), "rb") as _f:
                    questions = loader.load_question_bank(_f)

            st.session_state.question_bank = questions
            st.session_state._bank_source_key = bank_source_key
            st.session_state._bank_tag_names = tag_resolver.get_all_tag_names(
                questions, st.session_state.tag_map
            )
            # Clear category selection whenever the bank changes
            if "categories_input" in st.session_state:
                del st.session_state["categories_input"]

        except ValueError as e:
            st.error(str(e))
            # Leave previously loaded question_bank in place (do not clear it)

    if "question_bank" in st.session_state:
        # st.success(f"✓ {len(st.session_state.question_bank)} questions loaded.")  # hidden
        available_tags = st.session_state.get("_bank_tag_names", [])
    else:
        available_tags = []

with col2:
    # ---------------------------------------------------------------------------
    # T014: Optional scorecard upload (logic wired in Phase 7 / T035)
    # ---------------------------------------------------------------------------
    st.subheader("Previous Scorecard (optional)")
    uploaded_scorecard = st.file_uploader(
        "Upload previous scorecard to carry forward cumulative scores (.xlsx)",
        type=["xlsx"],
        key="scorecard_upload",
    )
    if uploaded_scorecard is not None:
        try:
            st.session_state.historical_scorecard = importer.load_scorecard(uploaded_scorecard)
            st.success("✓ Scorecard loaded. Cumulative scores will be carried forward.")
        except ValueError as e:
            st.error(str(e))
            st.session_state.historical_scorecard = None
    else:
        # Fall back to cumulative scores carried forward from the previous session
        st.session_state.historical_scorecard = st.session_state.get("_persistent_scorecard")

# ---------------------------------------------------------------------------
# T014: Category multiselect
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Categories")
st.info('Select TOGAF categories you want to practice', icon="ℹ️")
selected_categories = st.multiselect(
    "Choose categories…",
    options=available_tags,
    default=available_tags,
    disabled=len(available_tags) == 0,
    key="categories_input",
    placeholder="Load a question bank first" if not available_tags else "Choose categories…",
)

# ---------------------------------------------------------------------------
# T014: Start Session button (disabled until all conditions met)
# ---------------------------------------------------------------------------
st.divider()
bank_loaded = "question_bank" in st.session_state
name_filled = bool(user_name.strip())
cats_selected = len(selected_categories) > 0
can_start = bank_loaded and name_filled and cats_selected

start_btn = st.button(
    "▶ Start Session",
    disabled=not can_start,
    type="primary",
    use_container_width=True,
)

# ---------------------------------------------------------------------------
# T016: Start Session handler
# ---------------------------------------------------------------------------
if start_btn:
    # Resolve selected category names → integer tag ids
    tag_ids = [
        tid
        for name in selected_categories
        for tid in [tag_resolver.get_tag_id_for_name(name, st.session_state.tag_map)]
        if tid is not None
    ]

    filtered = loader.filter_by_tags(st.session_state.question_bank, tag_ids)

    try:
        drawn = loader.draw_session_questions(filtered, 8)
    except ValueError:
        st.error(
            f"Insufficient questions: only {len(filtered)} match the selected "
            "categories. Add more questions or broaden your tag selection."
        )
        st.stop()

    # Shuffle question order; shuffle options per question; build score lookups
    shuffled_qs = shuffler.shuffle_questions(drawn)
    shuffled_options_map = {}
    shuffle_maps_map = {}
    points_lookups_map = {}

    for q in shuffled_qs:
        q_id = q["id"]
        opts, smap = shuffler.shuffle_options(q)
        shuffled_options_map[q_id] = opts
        shuffle_maps_map[q_id] = smap
        points_lookups_map[q_id] = scoring.build_points_lookup(q["scoring"])

    # Write all session state keys
    st.session_state.user_name = user_name.strip()
    st.session_state.time_limit_seconds = 5400  # 90 minutes
    st.session_state.time_extension_used = False
    st.session_state.questions = shuffled_qs
    st.session_state.shuffled_options = shuffled_options_map
    st.session_state.shuffle_maps = shuffle_maps_map
    st.session_state.points_lookups = points_lookups_map
    st.session_state.session_active = True
    st.session_state.session_submitted = False
    st.session_state.current_question_idx = 0
    st.session_state.answers = {}
    st.session_state.flags = set()
    st.session_state.start_time = time.time()
    st.session_state.historical_scorecard = None  # wired in Phase 7 (T035)

    st.switch_page("pages/quiz.py")
