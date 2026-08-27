"""
Workout Plan Generator - Single Page Streamlit Application
Powered by Groq API and LLMs.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from workout_generator.models import UserProfile, PRESETS
from workout_generator.generator import generate_workout_plan, AVAILABLE_MODELS, DEFAULT_MODEL
from workout_generator.exercise_swap import swap_single_exercise

# Load environment variables (.env)
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Workout Plan Generator | Groq LLM",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .badge-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #EEF2FF;
        color: #4F46E5;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .injury-badge {
        background-color: #FEF2F2;
        color: #DC2626;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .stat-box {
        background: #F8FAFC;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #E2E8F0;
        text-align: center;
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
    st.header("⚙️ Configuration")
    
    # Check if key is available in environment
    env_api_key = os.environ.get("GROQ_API_KEY", "")
    
    groq_api_key = st.text_input(
        "Groq API Key",
        value=env_api_key,
        type="password",
        help="Get your free key at https://console.groq.com/keys",
        placeholder="gsk_..."
    )

    if groq_api_key:
        st.success("🔑 API Key configured", icon="✅")
    else:
        st.warning("⚠️ API Key needed to generate plans.", icon="🔑")

    st.markdown("---")
    st.subheader("🤖 Model & Sampling")
    
    selected_model = st.selectbox(
        "LLM Model",
        options=AVAILABLE_MODELS,
        index=0,
        help="Fast LLM inference models powered by Groq LPU."
    )

    temperature = st.slider(
        "Creativity / Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Lower values produce more deterministic, standardized plans; higher values offer variety."
    )

    st.markdown("---")
    st.subheader("⚡ Quick Presets (1-Click Test)")
    preset_choice = st.selectbox(
        "Load a sample profile:",
        options=["-- Select a preset --"] + list(PRESETS.keys()),
        index=0
    )

    st.markdown("---")
    st.caption("AI Engineering Cohort • Assignment 2")
    st.caption("Built with Streamlit & Groq API")


# Main UI Header
st.markdown('<div class="main-header">🏋️ AI Personalized Workout Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Design safe, structured, and science-based weekly workout plans tailored strictly to your goals, available equipment, and physical limitations.</div>',
    unsafe_allow_html=True,
)

# Apply Preset if selected
active_preset = PRESETS.get(preset_choice) if preset_choice != "-- Select a preset --" else None

# Input Form
with st.container():
    st.subheader("📋 Step 1: Your Fitness Profile & Constraints")
    
    col1, col2 = st.columns([1, 1])

    with col1:
        fitness_goal = st.selectbox(
            "🎯 Primary Fitness Goal *",
            options=[
                "Build muscle (Hypertrophy)",
                "Lose fat & tone",
                "General fitness & health",
                "Improve endurance & conditioning",
                "Strength & Power",
            ],
            index=0 if not active_preset else [
                "Build muscle (Hypertrophy)",
                "Lose fat & tone",
                "General fitness & health",
                "Improve endurance & conditioning",
                "Strength & Power",
            ].index(active_preset.fitness_goal) if active_preset.fitness_goal in [
                "Build muscle (Hypertrophy)",
                "Lose fat & tone",
                "General fitness & health",
                "Improve endurance & conditioning",
                "Strength & Power",
            ] else 1,
            help="Your main physical objective."
        )

        experience_level = st.select_slider(
            "📊 Experience Level *",
            options=["Beginner", "Intermediate", "Advanced"],
            value=active_preset.experience_level if active_preset else "Beginner",
            help="Calibrates workout volume, complexity of movements, and progression rate."
        )

        days_per_week = st.slider(
            "📅 Workout Days per Week *",
            min_value=1,
            max_value=7,
            value=active_preset.days_per_week if active_preset else 3,
            help="How many days per week you can commit to training."
        )

        session_duration = st.select_slider(
            "⏱️ Target Session Duration (Minutes) *",
            options=[20, 30, 45, 60, 75, 90],
            value=active_preset.session_duration_minutes if active_preset else 45,
            help="Time available per workout session."
        )

    with col2:
        equipment_options = [
            "No equipment (Bodyweight only)",
            "Home dumbbells & resistance bands",
            "Full gym (Barbells, dumbbells, cables, machines)",
        ]
        
        equipment_access = st.multiselect(
            "🛠️ Available Equipment *",
            options=equipment_options,
            default=active_preset.equipment_access if active_preset else [equipment_options[1]],
            help="Strict constraint: The AI will ONLY use equipment you select here."
        )

        split_preference = st.selectbox(
            "🔄 Preferred Workout Split",
            options=[
                "Trainer's Choice (Optimized)",
                "Full Body",
                "Upper / Lower Split",
                "Push / Pull / Legs",
                "Body-Part Specific Split",
            ],
            index=0 if not active_preset else (
                ["Trainer's Choice (Optimized)", "Full Body", "Upper / Lower Split", "Push / Pull / Legs", "Body-Part Specific Split"].index(active_preset.split_preference)
                if active_preset.split_preference in ["Trainer's Choice (Optimized)", "Full Body", "Upper / Lower Split", "Push / Pull / Legs", "Body-Part Specific Split"]
                else 0
            ),
            help="Choose your preferred structure or let the trainer pick the best split for your frequency."
        )

        injuries_or_limitations = st.text_area(
            "🩹 Injuries, Joint Pain or Physical Limitations (Optional)",
            value=active_preset.injuries_or_limitations if active_preset and active_preset.injuries_or_limitations else "",
            placeholder="e.g., Bad knees (avoid deep lunges), lower back pain, shoulder impingement on bench press...",
            help="Strict constraint: Exercises aggravating these will be excluded and safe alternatives provided."
        )

        additional_notes = st.text_input(
            "📝 Additional Preferences / Focus Areas (Optional)",
            value=active_preset.additional_notes if active_preset and active_preset.additional_notes else "",
            placeholder="e.g., Focus on glutes and upper back; prefer quiet home workouts...",
            help="Any extra instructions or focus areas."
        )

# Action Buttons
col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])

with col_btn1:
    generate_btn = st.button("🏋️ Generate Workout Plan", type="primary", use_container_width=True)

with col_btn2:
    regenerate_btn = st.button("🔄 Regenerate Variation", use_container_width=True, disabled=(st.session_state.generated_plan is None))

with col_btn3:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

if clear_btn:
    st.session_state.generated_plan = None
    st.session_state.current_profile = None
    st.session_state.generation_metadata = {}
    st.session_state.swap_results = None
    st.session_state.variation_count = 0
    st.rerun()

# Generation Execution Handler
if generate_btn or regenerate_btn:
    # 1. Check basic input validity
    if not equipment_access:
        st.error("⚠️ Please select at least one equipment option under Available Equipment.", icon="🚫")
    elif days_per_week < 1 or days_per_week > 7:
        st.error("⚠️ Days available per week must be between 1 and 7.", icon="🚫")
    else:
        # Create UserProfile instance
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
            st.error(f"⚠️ Validation error in user inputs: {str(e)}")
            profile = None

        if profile:
            if regenerate_btn:
                st.session_state.variation_count += 1
                seed = st.session_state.variation_count
                status_text = f"Regenerating fresh variation #{seed} with {selected_model}..."
            else:
                st.session_state.variation_count = 0
                seed = None
                status_text = f"Generating personalized workout plan with {selected_model}..."

            with st.spinner(status_text):
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
                st.success(f"✅ Workout plan generated successfully in {result.generation_time_sec}s!", icon="🎉")
            else:
                st.error(result.error_message, icon="❌")

# Display Results Section
if st.session_state.generated_plan:
    st.markdown("---")
    st.subheader("📋 Your Personalized Workout Plan")

    # Profile Summary Badges
    p = st.session_state.current_profile
    meta = st.session_state.generation_metadata

    badge_html = f"""
    <div style="margin-bottom: 1rem;">
        <span class="badge-tag">🎯 Goal: {p.fitness_goal}</span>
        <span class="badge-tag">📊 Level: {p.experience_level}</span>
        <span class="badge-tag">📅 Frequency: {p.days_per_week} Days/Wk</span>
        <span class="badge-tag">⏱️ Duration: ~{p.session_duration_minutes} min/session</span>
        <span class="badge-tag">🛠️ Equipment: {", ".join(p.equipment_access)}</span>
        {f'<span class="badge-tag injury-badge">🩹 Limitations: {p.injuries_or_limitations}</span>' if p.has_limitations() else ''}
        <span class="badge-tag" style="background-color: #F1F5F9; color: #475569;">🤖 Model: {meta.get('model', 'Groq')} ({meta.get('time_sec', 0)}s)</span>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

    # Download Buttons
    col_dl1, col_dl2, _ = st.columns([1.5, 1.5, 3])
    with col_dl1:
        st.download_button(
            label="📥 Download Plan (.md)",
            data=st.session_state.generated_plan,
            file_name=f"workout_plan_{p.fitness_goal.replace(' ', '_').lower()}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_dl2:
        st.download_button(
            label="📄 Download Plan (.txt)",
            data=st.session_state.generated_plan,
            file_name=f"workout_plan_{p.fitness_goal.replace(' ', '_').lower()}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # Render Markdown Content
    st.markdown(st.session_state.generated_plan)

    # Stretch Goal: Single Exercise Swapper Mini-Tool
    st.markdown("---")
    with st.expander("🔄 Exercise Swapper: Need to replace an exercise?", expanded=False):
        st.markdown(
            "If an exercise causes discomfort, requires equipment that's currently occupied, or you simply prefer an alternative, enter it below to get safe, biomechanically equivalent swaps."
        )
        
        swap_col1, swap_col2 = st.columns([2, 3])
        with swap_col1:
            exercise_to_swap = st.text_input(
                "Exercise Name to Replace",
                placeholder="e.g. Barbell Back Squat, Dumbbell Overhead Press"
            )
        with swap_col2:
            swap_reason = st.text_input(
                "Reason for Swap (Optional)",
                placeholder="e.g. Causes knee pinch, equipment busy, want dumbbell alternative"
            )
        
        swap_btn = st.button("🔍 Find Safe Alternatives", type="secondary")
        
        if swap_btn:
            if not exercise_to_swap:
                st.warning("Please specify the name of the exercise you want to replace.")
            else:
                with st.spinner("Finding safe, tailored alternatives..."):
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
            st.markdown("#### 💡 Alternative Exercise Options:")
            st.markdown(st.session_state.swap_results)
