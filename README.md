# QuizLit — TOGAF 10 Practitioner Exam Simulator

A free, open-source practice tool for candidates preparing for the **TOGAF 10 Practitioner** certification exam. Built with Python and Streamlit, it replicates the real exam's question style, partial-credit scoring model, and time pressure so you can study in conditions close to the actual test.

---

## Why This Exists

The TOGAF Practitioner exam is unlike most multiple-choice tests. Every question has a lengthy real-world scenario, and the four answer options are all plausible — they are scored on a gradient (5 / 3 / 1 / 0 points) rather than right-or-wrong. Most available practice tools don't reflect this. QuizLit does.

---

## Practice Online
[QuizLit-App](https://quizlit.itutul.com/) 

---

## Features

- **Realistic question format** — long scenario-based questions with four graduated answer options, matching the real exam style
- **Partial-credit scoring** — answers are graded 5 (best), 3 (second-best), 1 (third-best), or 0 (distractor), exactly as the real exam
- **90-minute countdown timer** — auto-submits when time expires
- **Shuffled every time** — question order and answer option order are randomised on each session so you can't memorise positions
- **Category filtering** — select specific TOGAF topic areas to focus your practice
- **Flag for review** — mark questions to revisit before submitting
- **Full rationale on results** — every option explained per question, with TOGAF standard references
- **Category breakdown chart** — horizontal bar chart of session vs. cumulative score by topic area
- **Strengths & Weaknesses pie charts** — visual snapshot of your best and worst topic areas across all sessions (up to 10 categories each)
- **Cumulative score tracking** — scores compound across sessions without any account or login; as long as you keep the browser open, your history carries forward automatically
- **Scorecard export** — download your results as an `.xlsx` file to keep a permanent record
- **Scorecard import** — upload a previous scorecard to carry cumulative scores across browser sessions
- **No registration, no data collection** — everything runs locally in your browser session

---

## Scoring Model

| Tier | Points |
|------|--------|
| Best answer | 5 |
| Second-best | 3 |
| Third-best | 1 |
| Distractor | 0 |

**8 questions × 5 points = 40 total. Pass mark: 24 / 40 (60%)**

---

## Running Locally

**Requirements:** Python 3.11+

```bash
# 1. Clone the repo
git clone https://github.com/your-username/QuizLit.git
cd QuizLit

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Project Structure

```
app.py                  ← Entry point (Streamlit page router)
pages/
  setup.py              ← Session configuration & launch
  quiz.py               ← Timed quiz session
  results.py            ← Score review & download
components/
  question_card.py      ← Question + answer radio widget
  navigator.py          ← Sidebar question navigator
  timer.py              ← Countdown timer
  category_chart.py     ← Bar chart + Strengths/Weaknesses pie charts
logic/
  scoring.py            ← Partial-credit scoring, pass/fail, category breakdown
  shuffler.py           ← Question and option shuffling
  exporter.py           ← Excel scorecard builder
  importer.py           ← Excel scorecard parser
data/
  loader.py             ← Question bank loader & validator
  tag_resolver.py       ← TOGAF topic tag lookup
bank/
  Q1.json               ← Bundled question bank
togaf_tags_db.csv       ← TOGAF topic tag reference
```

---

## Question Bank Format

Questions are stored as JSON arrays. Each question follows this schema:

```json
{
  "id": 1,
  "scenario": "A long real-world scenario paragraph...",
  "question": "Based on the scenario, which is the best answer?",
  "options": {
    "A": "Option text...",
    "B": "Option text...",
    "C": "Option text...",
    "D": "Option text..."
  },
  "scoring": {
    "best":        { "option": "A", "points": 5 },
    "second_best": { "option": "D", "points": 3 },
    "third_best":  { "option": "C", "points": 1 },
    "distractor":  { "option": "B", "points": 0 }
  },
  "tags": [2, 19, 67],
  "rationale": {
    "why_best": "...",
    "why_second_best": "...",
    "why_third_best": "...",
    "why_distractor": "...",
    "concept_tested": "...",
    "common_mistakes": "...",
    "togaf_reference": "TOGAF Standard, 10th Edition, ..."
  }
}
```

All four point values (5, 3, 1, 0) must appear exactly once in `scoring`. Tag IDs must match entries in `togaf_tags_db.csv`.

---

## Adding Your Own Questions

You can upload a custom `.json` question bank directly in the app without modifying any code. The file must follow the schema above and pass validation before the session can start.

---

## Tech Stack

| Layer | Library |
|-------|---------|
| UI | [Streamlit](https://streamlit.io) |
| Charts | [Matplotlib](https://matplotlib.org) |
| Spreadsheet I/O | [openpyxl](https://openpyxl.readthedocs.io) |
| Data | [pandas](https://pandas.pydata.org) |
| Tests | [pytest](https://pytest.org) |

---

## Running Tests

```bash
pytest
```

---

## Disclaimer

This project is not affiliated with, endorsed by, or associated with The Open Group or the official TOGAF certification programme. TOGAF is a registered trademark of The Open Group. This tool is intended for self-study purposes only.

---

## License

MIT
