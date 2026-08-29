"""
Personalized Workout Plan Generator - Single Page Web Application
Authored by Shubradip.

Engineered with Streamlit and Groq LLM API.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from workout_generator.models import UserProfile, PRESETS
from workout_generator.generator import generate_workout_plan, AVAILABLE_MODELS, DEFAULT_MODEL
from workout_generator.exercise_swap import swap_single_exercise

# Load environment configuration
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Personalized Workout Plan Generator",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .badge-tag {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #EEF2FF;
        color: #4338CA;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid #C7D2FE;
    }
    .injury-badge {
        background-color: #FEF2F2;
        color: #B91C1C;
        border-color: #FECACA;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = None
if "current_profile" not in st.session_state:
    st.session_state.current_profile = None
if "generation_metadata" not in st.session_state:
    st.session_state.generation_metadata = {}
if "variation_count" not in st.session_state:
    st.session_state.variation_count = 0
if "swap_results" not in st.session_state:
    st.session_state.swap_results = None

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    
    env_api_key = os.environ.get("GROQ_API_KEY", "")
    
    groq_api_key = st.text_input(
        "Groq API Key",
        value=env_api_key,
        type="password",
        help="Access key from console.groq.com",
        placeholder="gsk_..."
    )

    if groq_api_key:
        st.success("API Key configured")
    else:
        st.warning("API Key required to generate workouts.")

    st.markdown("---")
    st.subheader("Model and Parameters")
    
    selected_model = st.selectbox(
        "LLM Inference Model",
        options=AVAILABLE_MODELS,
        index=0,
        help="High-speed reasoning model endpoints via Groq LPU."
    )

    temperature = st.slider(
        "Sampling Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Controls output diversity: lower values are more deterministic, higher values produce greater variety."
    )

    st.markdown("---")
    st.subheader("Evaluation Presets")
    preset_choice = st.selectbox(
        "Load sample profile:",
        options=["-- Select a preset --"] + list(PRESETS.keys()),
        index=0
    )

    st.markdown("---")
    st.caption("AI Engineering Cohort • Assignment 2")
    st.caption("Developed by Shubradip")


# Main Header
st.markdown('<div class="main-header">Personalized Workout Plan Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Evidence-based weekly workout programming tailored to your goals, equipment, and physical constraints.</div>',
    unsafe_allow_html=True,
)

# Apply Preset if selected
active_preset = PRESETS.get(preset_choice) if preset_choice != "-- Select a preset --" else None

# Input Form
with st.container():
    st.subheader("Step 1: Fitness Profile and Constraints")
    
    col1, col2 = st.columns([1, 1])

    with col1:
        fitness_goal = st.selectbox(
            "Primary Fitness Goal",
            options=[
                "Build Muscle (Hypertrophy)",
                "Lose Fat and Lean Conditioning",
                "General Fitness and Health",
                "Improve Endurance and Conditioning",
                "Strength and Power Development",
            ],
            index=0 if not active_preset else [
                "Build Muscle (Hypertrophy)",
                "Lose Fat and Lean Conditioning",
                "General Fitness and Health",
                "Improve Endurance and Conditioning",
                "Strength and Power Development",
            ].index(active_preset.fitness_goal) if active_preset.fitness_goal in [
                "Build Muscle (Hypertrophy)",
                "Lose Fat and Lean Conditioning",
                "General Fitness and Health",
                "Improve Endurance and Conditioning",
                "Strength and Power Development",
            ] else 0,
            help="Your primary athletic or physical objective."
        )

        experience_level = st.select_slider(
            "Experience Level",
            options=["Beginner", "Intermediate", "Advanced"],
            value=active_preset.experience_level if active_preset else "Beginner",
            help="Calibrates weekly volume, movement complexity, and loading intensity."
        )

        days_per_week = st.slider(
            "Workout Days per Week",
            min_value=1,
            max_value=7,
            value=active_preset.days_per_week if active_preset else 3,
            help="Weekly training frequency committed."
        )

        session_duration = st.select_slider(
            "Target Session Duration (Minutes)",
            options=[20, 30, 45, 60, 75, 90],
            value=active_preset.session_duration_minutes if active_preset else 45,
            help="Available time per training session."
        )

    with col2:
        equipment_options = [
            "Bodyweight Calisthenics Only",
            "Home Dumbbells and Resistance Bands",
            "Full Commercial Gym (Barbells, Dumbbells, Cables, Machines)",
        ]
        
        equipment_access = st.multiselect(
            "Available Equipment",
            options=equipment_options,
            default=active_preset.equipment_access if active_preset else [equipment_options[1]],
            help="Strict boundary: The generator will only select movements matching this equipment."
        )

        split_preference = st.selectbox(
            "Preferred Workout Split",
            options=[
                "Trainer Optimized Split",
                "Full Body",
                "Upper / Lower Split",
                "Push / Pull / Legs",
                "Body-Part Specific Split",
            ],
            index=0 if not active_preset else (
                ["Trainer Optimized Split", "Full Body", "Upper / Lower Split", "Push / Pull / Legs", "Body-Part Specific Split"].index(active_preset.split_preference)
                if active_preset.split_preference in ["Trainer Optimized Split", "Full Body", "Upper / Lower Split", "Push / Pull / Legs", "Body-Part Specific Split"]
                else 0
            ),
            help="Split architecture or automated optimization based on frequency."
        )

        injuries_or_limitations = st.text_area(
            "Injuries or Physical Limitations (Optional)",
            value=active_preset.injuries_or_limitations if active_preset and active_preset.injuries_or_limitations else "",
            placeholder="e.g., Patellar tendonitis (avoid deep knee flexion), lower back pain, anterior shoulder impingement...",
            help="Strict boundary: Movements placing shear stress on these areas are excluded in favor of safe alternatives."
        )

        additional_notes = st.text_input(
            "Additional Preferences or Focus Areas (Optional)",
            value=active_preset.additional_notes if active_preset and active_preset.additional_notes else "",
            placeholder="e.g., Focus on upper back and glutes; prefer low noise home routines...",
            help="Optional personalization notes."
        )

# Action Buttons
col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])

with col_btn1:
    generate_btn = st.button("Generate Workout Plan", type="primary", use_container_width=True)

with col_btn2:
    regenerate_btn = st.button("Regenerate Variation", use_container_width=True, disabled=(st.session_state.generated_plan is None))

with col_btn3:
    clear_btn = st.button("Clear Results", use_container_width=True)

if clear_btn:
    st.session_state.generated_plan = None
    st.session_state.current_profile = None
    st.session_state.generation_metadata = {}
    st.session_state.swap_results = None
    st.session_state.variation_count = 0
    st.rerun()

# Execution Handler
if generate_btn or regenerate_btn:
    if not equipment_access:
        st.error("Please select at least one equipment option.")
    elif days_per_week < 1 or days_per_week > 7:
        st.error("Training frequency must be between 1 and 7 days per week.")
    else:
        try:
            profile = UserProfile(
                fitness_goal=fitness_goal,
                experience_level=experience_level,
                days_per_week=days_per_week,
                equipment_access=equipment_access,
                session_duration_minutes=session_duration,
                split_preference=split_preference,
                injuries_or_limitations=injuries_or_limitations,
                additional_notes=additional_notes,
            )
        except Exception as e:
            st.error(f"Input validation error: {str(e)}")
            profile = None

        if profile:
            if regenerate_btn:
                st.session_state.variation_count += 1
                seed = st.session_state.variation_count
                status_msg = f"Generating variation #{seed} using {selected_model}..."
            else:
                st.session_state.variation_count = 0
                seed = None
                status_msg = f"Generating structured workout program using {selected_model}..."

            with st.spinner(status_msg):
                result = generate_workout_plan(
                    profile=profile,
                    api_key=groq_api_key,
                    model=selected_model,
                    temperature=temperature,
                    variation_seed=seed,
                )

            if result.success:
                st.session_state.generated_plan = result.plan_markdown
                st.session_state.current_profile = profile
                st.session_state.generation_metadata = {
                    "model": result.model_used,
                    "time_sec": result.generation_time_sec,
                    "variation": st.session_state.variation_count,
                }
                st.session_state.swap_results = None
                st.success(f"Workout program generated successfully in {result.generation_time_sec}s")
            else:
                st.error(result.error_message)

# Results Presentation
if st.session_state.generated_plan:
    st.markdown("---")
    st.subheader("Your Generated Workout Program")

    p = st.session_state.current_profile
    meta = st.session_state.generation_metadata

    badge_html = f"""
    <div style="margin-bottom: 1rem;">
        <span class="badge-tag">Goal: {p.fitness_goal}</span>
        <span class="badge-tag">Level: {p.experience_level}</span>
        <span class="badge-tag">Frequency: {p.days_per_week} Days/Week</span>
        <span class="badge-tag">Duration: ~{p.session_duration_minutes} min/session</span>
        <span class="badge-tag">Equipment: {", ".join(p.equipment_access)}</span>
        {f'<span class="badge-tag injury-badge">Limitations: {p.injuries_or_limitations}</span>' if p.has_limitations() else ''}
        <span class="badge-tag" style="background-color: #F8FAFC; color: #334155; border-color: #E2E8F0;">Model: {meta.get('model', 'Groq')} ({meta.get('time_sec', 0)}s)</span>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

    # Export Buttons
    col_dl1, col_dl2, _ = st.columns([1.5, 1.5, 3])
    with col_dl1:
        st.download_button(
            label="Download Plan (.md)",
            data=st.session_state.generated_plan,
            file_name=f"workout_program_{p.fitness_goal.replace(' ', '_').lower()}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_dl2:
        st.download_button(
            label="Download Plan (.txt)",
            data=st.session_state.generated_plan,
            file_name=f"workout_program_{p.fitness_goal.replace(' ', '_').lower()}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # Render Program
    st.markdown(st.session_state.generated_plan)

    # Exercise Substitution Tool
    st.markdown("---")
    with st.expander("Exercise Substitution Tool", expanded=False):
        st.markdown(
            "Substitute any exercise from your program with biomechanically equivalent alternatives matching your equipment and injury constraints."
        )
        
        swap_col1, swap_col2 = st.columns([2, 3])
        with swap_col1:
            exercise_to_swap = st.text_input(
                "Exercise Name to Substitute",
                placeholder="e.g., Barbell Back Squat, Dumbbell Shoulder Press"
            )
        with swap_col2:
            swap_reason = st.text_input(
                "Reason for Substitution (Optional)",
                placeholder="e.g., Knee discomfort, equipment unavailable, prefer dumbbell variant"
            )
        
        swap_btn = st.button("Find Alternative Exercises", type="secondary")
        
        if swap_btn:
            if not exercise_to_swap:
                st.warning("Please specify the name of the exercise to substitute.")
            else:
                with st.spinner("Analyzing biomechanical alternatives..."):
                    swap_res = swap_single_exercise(
                        original_exercise=exercise_to_swap,
                        reason=swap_reason,
                        profile=st.session_state.current_profile,
                        api_key=groq_api_key,
                        model=selected_model,
                    )
                if swap_res.success:
                    st.session_state.swap_results = swap_res.replacement_markdown
                else:
                    st.error(swap_res.error_message)

        if st.session_state.swap_results:
            st.markdown("#### Alternative Exercise Options:")
            st.markdown(st.session_state.swap_results)
