"""
Prompt engineering module for the Workout Plan Generator.
Contains meticulously designed system and user prompts to guarantee constraint
adherence, biomechanical safety, structured formatting, and actionable workouts.
"""

from typing import Optional
from .models import UserProfile


SYSTEM_PROMPT = """You are an elite, NSCA-Certified Strength and Conditioning Specialist (CSCS) and Doctor of Physical Therapy (DPT).
Your mission is to design a highly personalized, practical, safe, and scientifically grounded weekly workout plan based strictly on the user's profile and constraints.

### NON-NEGOTIABLE RULES & CONSTRAINTS:
1. **EQUIPMENT COMPLIANCE (ZERO TOLERANCE FOR VIOLATIONS)**:
   - ONLY prescribe exercises possible with the user's specified equipment.
   - If "No equipment (Bodyweight only)": DO NOT suggest barbells, dumbbells, cables, or machines. Use only bodyweight, calisthenics, and household items if applicable.
   - If "Home dumbbells & resistance bands": DO NOT prescribe barbell lifts, cable crossovers, or commercial machines.
   - If "Full gym": You may use barbells, dumbbells, cables, and machines appropriately.

2. **INJURIES & LIMITATIONS SAFETY (CRITICAL)**:
   - If the user specifies an injury or physical limitation (e.g., "bad knees", "lower back pain", "shoulder impingement"):
     a) NEVER prescribe exercises that aggravate the affected area (e.g., avoid overhead pressing for shoulder impingement, avoid deep unassisted lunges/leg extensions for knee tendonitis, avoid heavy spinal compression for lower back issues).
     b) Provide safe, biomechanically sound substitutions with explicit coaching notes explaining WHY the exercise is joint-friendly.
     c) Add a mandatory, clear **Medical Disclaimer** at the end advising clearance from a qualified healthcare provider.

3. **WEEKLY STRUCTURE & SCHEDULE**:
   - Generate an exact weekly schedule matching the user's `days_per_week` training days, plus recommended active recovery/rest days for the remaining days.
   - Calibrate total volume, exercise selection, and rest periods to match their `experience_level` and `session_duration_minutes`.

4. **FORMATTING & ACTIONABILITY**:
   - Do NOT produce a vague wall of text or generic advice like "do some squats".
   - Use clear markdown headers, bullet points, and tables.
   - For every exercise, provide:
     - **Exercise Name** (with exact variation)
     - **Primary Muscle Worked**
     - **Sets x Reps** (calibrated to goal)
     - **Rest Period** (e.g., 60-90s)
     - **Target RPE / Intensity** (Rate of Perceived Exertion on a 1-10 scale)
     - **Key Form Cue / Safe Execution Tip**
"""


def build_workout_prompt(profile: UserProfile, variation_seed: Optional[int] = None) -> str:
    """
    Constructs a detailed prompt from the structured UserProfile.
    """
    equipment_str = ", ".join(profile.equipment_access)
    limitations_str = (
        profile.injuries_or_limitations.strip()
        if profile.injuries_or_limitations and profile.injuries_or_limitations.strip()
        else "None reported (Fully healthy, no movement restrictions)"
    )
    notes_str = (
        profile.additional_notes.strip()
        if profile.additional_notes and profile.additional_notes.strip()
        else "None"
    )

    variation_instruction = ""
    if variation_seed is not None:
        variation_instruction = f"""
*Note: This is generation variation #{variation_seed}. Provide a fresh alternative variation of exercise selections, split sequencing, or intensity techniques while strictly honoring all constraints.*
"""

    return f"""Please create a complete, personalized weekly workout plan based on the following structured user profile:

### USER PROFILE & CONSTRAINTS:
- **Primary Fitness Goal**: {profile.fitness_goal}
- **Experience Level**: {profile.experience_level}
- **Training Frequency**: {profile.days_per_week} days per week
- **Available Equipment**: {equipment_str}
- **Target Session Duration**: {profile.session_duration_minutes} minutes per workout
- **Preferred Split**: {profile.split_preference or "Trainer's Choice (Optimized)"}
- **Reported Injuries / Limitations**: {limitations_str}
- **Additional Preferences / Focus**: {notes_str}
{variation_instruction}

---

### REQUIRED OUTPUT FORMAT:

Please structure your response cleanly into the following 4 sections:

## 1. 📋 Program Overview & Strategy
- **Split Summary**: Explain the chosen split and why it matches {profile.days_per_week} days/week and the {profile.fitness_goal} goal.
- **Weekly Schedule Matrix**: A concise day-by-day table (e.g. Day 1: Push / Day 2: Pull / Day 3: Rest...).
- **Estimated Session Duration**: Confirming fit within ~{profile.session_duration_minutes} minutes.

## 2. 🏋️ Day-by-Day Detailed Workout Plan
For EACH of the {profile.days_per_week} training days, provide:
### **Day [X]: [Workout Title / Focus]**
- **Dynamic Warm-Up (3-5 min)**: 3 specific mobility/activation drills preparing for today's movements.
- **Main Workout**:
  | # | Exercise Name | Target Muscle | Sets | Reps | Rest | RPE (1-10) | Key Form Cue |
  |---|---|---|---|---|---|---|---|
  *(Provide 4-6 exercises perfectly suited to {equipment_str} and avoiding {limitations_str})*
- **Cool-Down & Joint Mobility (2-3 min)**: Specific stretches for recovery.

*(For the non-training days, specify Active Recovery, Zone 2 light cardio, or Full Rest guidance).*

## 3. 📈 Progressive Overload & Coaching Guidelines
- **How to Progress (Weeks 1-4)**: Clear rules on when and how to increase weight, reps, or tempo.
- **Recovery & Hydration Rules**: Actionable advice to support recovery for {profile.experience_level} level.

## 4. ⚠️ Safety, Injury Adaptations & Disclaimer
- **Injury Adaptations Made**: Specifically highlight how the plan modified movements to safeguard against: "{limitations_str}".
- **Medical Disclaimer**: {"A clear medical disclaimer indicating this is educational fitness guidance and not medical diagnosis or prescription." if profile.has_limitations() else "Standard physical activity safety disclaimer."}
"""


def build_exercise_swap_prompt(
    original_exercise: str,
    reason: str,
    profile: UserProfile
) -> str:
    """
    Constructs a prompt to generate 2-3 safe, biomechanically equivalent exercise replacements.
    """
    equipment_str = ", ".join(profile.equipment_access)
    limitations_str = (
        profile.injuries_or_limitations.strip()
        if profile.injuries_or_limitations and profile.injuries_or_limitations.strip()
        else "None"
    )

    return f"""A user wants to replace an exercise in their workout plan.
Provide 2-3 optimal alternative exercises that match their constraints.

### Context:
- **Exercise to Replace**: {original_exercise}
- **Reason for Swap**: {reason}
- **User's Fitness Goal**: {profile.fitness_goal}
- **Experience Level**: {profile.experience_level}
- **Available Equipment**: {equipment_str} (STRICT CONSTRAINT: ONLY suggest exercises using this equipment)
- **Injuries / Limitations**: {limitations_str} (STRICT CONSTRAINT: DO NOT aggravate these areas)

### Output Format:
For each of the 2-3 alternatives, provide:
1. **Alternative Name & Equipment Needed**
2. **Why it's a great substitute** (movement pattern & muscle target match)
3. **Recommended Sets, Reps, and Rest**
4. **Coaching Cue for safe execution**
"""
