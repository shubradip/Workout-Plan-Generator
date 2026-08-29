# Personalized Workout Plan Generator

> AI Engineering Cohort — Assignment 2  
> **Author:** Shubradip  
> **Repository:** [https://github.com/shubradip/Workout-Plan-Generator](https://github.com/shubradip/Workout-Plan-Generator)

A production-grade, single-page Streamlit application that collects structured fitness parameters and leverages Groq LLM inference to generate personalized, periodized, and biomechanically safe weekly workout programs.

---

## Architectural Overview

This system moves beyond basic prompt concatenation by implementing a domain-grounded prompt engineering architecture. The model is conditioned with a certified personal trainer (CSCS) and physical therapy (DPT) persona to enforce strict constraint isolation, injury safeguards, and volume calibration.

### Core Features

1. **Structured Input Validation:**
   - Primary Fitness Goal (Hypertrophy, Fat Loss, Endurance, Strength Development)
   - Experience Level (Beginner, Intermediate, Advanced)
   - Training Frequency (1 to 7 days per week)
   - Equipment Access (Bodyweight Only, Home Dumbbells and Bands, Full Commercial Gym)
   - Target Session Duration (20 to 90 minutes)
   - Split Architecture (Full Body, Upper/Lower, Push/Pull/Legs, Trainer Optimized)
   - Musculoskeletal Limitations & Injury History (Free-text with targeted biomechanical handling)

2. **Deterministic Constraint Enforcement:**
   - **Equipment Isolation:** Strictly eliminates hallucinations of unavailable training equipment.
   - **Biomechanical Safety:** Automatically identifies contraindicated movement patterns (e.g., knee shear, spinal axial loading, shoulder impingement) and provides safe replacements with form cues and medical disclaimers.
   - **Structured Markdown Tables:** Outputs comprehensive day-by-day routines specifying Exercise, Muscle Group, Sets, Reps, Rest Intervals, RPE (1-10), and Form Cues.

3. **System Resilience & Error Recovery:**
   - Input validation handled via Pydantic v2 schemas before triggering API calls.
   - Comprehensive `try...except` exception boundaries for `groq.AuthenticationError`, `groq.RateLimitError` (HTTP 429), and `groq.APIConnectionError`.
   - Empty/malformed payload fallback detection.

4. **Interactive Application Features:**
   - **Regenerate Variation:** Generates alternative split variations while preserving user profile parameters.
   - **Session State Persistence:** Retains generated routines across UI interactions using `st.session_state`.
   - **Export Formats:** Direct one-click download handlers for Markdown (`.md`) and Plain Text (`.txt`).
   - **Exercise Substitution Tool:** On-the-fly single movement replacer providing joint-safe alternatives.
   - **Evaluation Presets:** Pre-configured benchmark profiles for rapid assessment.

---

## Project Structure

```
workout-plan-generator/
├── app.py                      # Streamlit frontend with reactive state management
├── workout_generator/
│   ├── __init__.py             # Public module interface
│   ├── models.py               # Pydantic v2 domain schemas (UserProfile, GenerationResult, SwapResult)
│   ├── prompts.py              # Prompt compilation engine and constraint templates
│   ├── generator.py            # Type-annotated Groq API integration layer
│   └── exercise_swap.py        # Targeted exercise replacement module
├── tests/
│   ├── __init__.py
│   └── test_generator.py       # 17 automated unit tests (Pytest / Unittest)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable configuration template
├── .gitignore                  # Git ignore rules
├── run.bat                     # Windows application launcher script
├── generate_guide_pdf.py       # Technical PDF documentation builder
└── README.md                   # System documentation and rubric alignment
```

---

## Setup and Execution Guide

### 1. Clone Repository
```bash
git clone https://github.com/shubradip/Workout-Plan-Generator.git
cd Workout-Plan-Generator
```

### 2. Environment Setup
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Configure your Groq API key in a `.env` file or directly inside the Streamlit application sidebar:
```bash
cp .env.example .env
# Edit .env and supply your GROQ_API_KEY
```

### 5. Launch the Application
```bash
streamlit run app.py
```
*(On Windows, you can also launch the application by running `run.bat`)*

---

## Test Suite Execution

The repository includes 17 unit tests verifying domain validation, prompt construction, mock API behavior, and defensive exception handling:

```bash
# Run with Pytest
pytest tests/ -v

# Run with standard Unittest
python -m unittest discover -s tests -v
```

---

## Assignment Rubric Alignment

| Rubric Criteria | Weight | Implementation Details |
|---|---|---|
| **Defensive Input Validation** | 20% | Pydantic model validation (`UserProfile`) and UI alert banners prevent unhandled crashes on invalid inputs. |
| **Structured Input Mapping** | 25% | Multi-field parameters mapped into prompt compilation functions with type safety. |
| **Prompt Design & Constraint Enforcement** | 30% | CSCS persona, equipment isolation, biomechanical injury substitutions, and medical disclaimers. |
| **API Error Resilience** | 15% | Explicit `try...except` handling for authentication, rate limit, and network exceptions. |
| **Code Quality & Testing** | 10% | Fully modular architecture, 100% type annotations, docstrings, and 17 passing unit tests. |

---

## Technical Specifications
- **Language:** Python 3.9+
- **Web Framework:** Streamlit
- **LLM Engine:** Groq API (`qwen/qwen3.8-27b`, `qwen/qwen3.6-27b`, `openai/gpt-oss-120b`)
- **Data Validation:** Pydantic v2
- **Testing:** Pytest / Python Unittest
