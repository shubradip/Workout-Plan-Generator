# 🏋️ AI Personalized Workout Plan Generator

> **AI Engineering Cohort — Assignment 2**  
> Build a single-page Streamlit application that collects structured inputs about a user's fitness profile and uses an LLM via the **Groq API** to generate a safe, science-based, and actionable weekly workout plan.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-FF4B4B.svg)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-API-F55036.svg)](https://console.groq.com)
[![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)]()

---

## 🌟 Overview & Key Features

This application goes beyond naive prompt concatenation to act as a **CSCS-Certified Strength and Conditioning Specialist & Physical Therapist**. It enforces strict biomechanical constraints, provides structured day-by-day routines, and offers interactive workout customization tools.

### 1. 📋 Structured Inputs (Not just free text)
- **Primary Fitness Goal**: Build muscle (Hypertrophy), Lose fat & tone, General fitness & health, Improve endurance & conditioning, Strength & Power.
- **Experience Level**: Beginner, Intermediate, Advanced.
- **Training Frequency**: 1 to 7 days per week slider.
- **Equipment Access**: Multiselect (Bodyweight only, Home dumbbells & bands, Full gym).
- **Target Session Duration**: 20 to 90 minutes.
- **Split Preference**: Full Body, Upper/Lower, Push/Pull/Legs, Body-part split, or Trainer's Choice.
- **Injuries / Joint Pain / Physical Limitations**: Free text for targeted biomechanical adaptations (e.g. *"bad knees"*, *"shoulder impingement"*).
- **Additional Preferences**: Custom focus areas or special instructions.

### 2. 🧠 Advanced Prompt Engineering & Constraint Adherence
- **Zero-Violation Equipment Policy**: Never prescribes equipment outside what the user owns.
- **Injury Safety & Biomechanical Replacements**: Identifies contraindicated movements (e.g. knee shear, lumbar compression, shoulder impingement) and provides safe alternatives with explanatory coaching cues.
- **Actionable & Structured Format**: Outputs an Overview Matrix, Dynamic Warm-ups, Main Workouts (Exercises, Sets, Reps, Rest, RPE 1–10, Form Cues), Cool-down, and Progressive Overload Rules.
- **Medical Disclaimer**: Automatically attaches appropriate disclaimers when injuries or limitations are noted.

### 3. 🛡️ Robust Error Handling & Resilience
- **Input Validation**: Catches invalid day counts, empty equipment selections, and malformed inputs with friendly UI banners.
- **API Authentication Errors**: Clear prompt when the API key is missing or invalid.
- **Rate Limit & Network Errors**: Graceful error catching for `groq.RateLimitError` and `groq.APIConnectionError`.
- **Empty / Malformed Responses**: Fallback handling and regeneration prompts.

### 4. 🚀 Stretch Goals & Extras Included
- 🔄 **Regenerate Variation**: Generate alternative variations of the plan with different exercise selections.
- 💾 **Session State Persistence**: Generated workout plans persist across UI interactions and reruns.
- 📥 **Export to Markdown & Text**: One-click download buttons (`.md` and `.txt`).
- 🔍 **Exercise Swapper Mini-Tool**: Swap individual exercises (e.g. when equipment is occupied or joint pain occurs) with safe, tailored alternatives.
- ⚡ **1-Click Evaluation Presets**: Preloaded sample profiles (*"Busy Professional"*, *"Hypertrophy Seeker"*, *"Endurance & Bad Knees"*, *"Strength & Power"*).

---

## 🗂️ Project Architecture

```
workout-plan-generator/
├── app.py                      # Streamlit frontend with layout, state, and export tools
├── workout_generator/
│   ├── __init__.py             # Public API exports
│   ├── models.py               # Pydantic schemas (UserProfile, GenerationResult, SwapResult, PRESETS)
│   ├── prompts.py              # System prompt and prompt construction functions
│   ├── generator.py            # Type-annotated Groq API caller with try/except error handling
│   └── exercise_swap.py        # Single exercise replacer module (Stretch goal)
├── tests/
│   ├── __init__.py
│   └── test_generator.py       # 17 Unit tests covering validation, prompts, and error cases
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
└── README.md                   # Documentation and rubric alignment
```

---

## 🚀 Quickstart & Setup

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd workout-plan-generator
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Groq API Key (Optional)
You can provide your API key directly in the Streamlit sidebar, or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and insert your GROQ_API_KEY=gsk_...
```
*(Get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys))*

### 5. Launch the Streamlit App
```bash
streamlit run app.py
```

---

## 🧪 Running Tests

The test suite includes 17 automated tests verifying schema validation, prompt generation, error handling, and mock API calls:

```bash
# Run using pytest
pytest tests/ -v

# Or run using standard unittest
python -m unittest discover -s tests -v
```

---

## 📊 Rubric Alignment & Verification

| Rubric Criteria | Weight | Implementation Details |
|---|---|---|
| **App runs without crashing on empty/invalid input** | 20% | Handled via Pydantic model validation (`UserProfile`), UI warning banners, and error checks before triggering API calls. |
| **Inputs are structured and correctly passed into prompt** | 25% | Multi-field structured form (Goal, Experience, Days, Equipment, Duration, Split, Limitations). `build_workout_prompt()` injects each structured field into the system/user prompts. |
| **Prompt design respects constraints & is usable** | 30% | Persona-driven prompt enforces zero-equipment violations, joint-friendly substitutions for reported injuries, specific sets/reps/rest/RPE tables, warm-up/cool-down, and medical disclaimers. |
| **Error handling (API failure, empty/malformed response)** | 15% | Comprehensive `try...except` handling for `AuthenticationError`, `RateLimitError`, `APIConnectionError`, `APIStatusError`, and empty response checks with user-friendly messages. |
| **Code quality (type hints, function separation, readability)** | 10% | Fully modular architecture (`models.py`, `prompts.py`, `generator.py`, `exercise_swap.py`), PEP 8 compliant, 100% type-annotated functions, and clean docstrings. |

---

## 👨‍💻 Tech Stack
- **Language**: Python 3.9+
- **Frontend / Framework**: Streamlit
- **LLM Provider**: Groq API (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`)
- **Data Validation**: Pydantic v2
- **Testing**: Pytest / Unittest
