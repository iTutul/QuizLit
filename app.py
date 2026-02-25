import streamlit as st

st.set_page_config(layout="wide")

setup_page = st.Page("pages/setup.py", title="Session Setup", icon="⚙️")
quiz_page = st.Page("pages/quiz.py", title="Quiz", icon="📝")
results_page = st.Page("pages/results.py", title="Results", icon="📊")

pg = st.navigation([setup_page, quiz_page, results_page])
pg.run()
