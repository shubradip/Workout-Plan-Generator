"""
Prompt engineering architecture and constraint validation module.
Authored by Shubradip.

This module formats structured user parameters into high-precision,
constraint-enforced prompt instructions for the LLM inference engine.
"""

from typing import Optional
from .models import UserProfile


SYSTEM_PROMPT = """You are an elite, NSCA-Certified Strength and Conditioning Specialist (CSCS) and Doctor of Physical Therapy (DPT).
Your objective is to design an evidence-based, periodized, safe, and actionable weekly workout program tailored strictly to the trainee's profile and constraints.

NON-NEGOTIABLE OPERATIONAL CONSTRAINTS:
1. EQUIPMENT ISOLATION:
   - Prescribe ONLY exercises that can be performed with the specified equipment.
   - If 'Bodyweight Calisthenics Only': Do not prescribe barbells, dumbbells, cables, or machines.
   - If 'Home Dumbbells and Resistance Bands': Do not prescribe barbell compound lifts or specialized commercial gym machinery.
   - If 'Full Commercial Gym': Utilize barbells, dumbbells, cables, and machines where appropriate.

2. INJURY PREVENTION AND BIOMECHANICAL ADAPTATIONS:
   - If the user reports injuries, joint discomfort, or movement limitations:
     a) Completely avoid movement patterns that impose shear stress or axial compression on the affected joint.
     b) Provide biomechanically sound substitutions with concise coaching cues explaining the joint-friendly adaptation.
     c) Include an explicit Medical Disclaimer at the end of the program.

3. VOLUME AND FREQUENCY ALLOCATION:
   - Design a complete weekly schedule matching the exact training frequency (days per week) requested.
   - Structure non-training days as scheduled rest, active recovery, or mobility sessions.
   - Calibrate volume (sets/reps) and intensity according to the trainee's experience level and session duration.

4. CLEAN STRUCTURED FORMATTING:
   - Do not output vague summaries or walls of unstructured prose.
   - Use clean Markdown headers and tabular formatting without decorative emojis or icons in headings.
   - For every prescribed exercise, specify: Exercise Name, Target Muscle, Sets, Reps, Rest Interval, RPE (Rate of Perceived Exertion 1-10), and 1-2 Essential Form Cues.
"""


def build_workout_prompt(profile: UserProfile, variation_seed: Optional[int] = None) -> str:
    """
    Assembles a comprehensive prompt from a validated UserProfile instance.
    """
    equipment_str = ", ".join(profile.equipment_access)
    limitations_str = (
        profile.injuries_or_limitations.strip()
        if profile.injuries_or_limitations and profile.injuries_or_limitations.strip()
        else "None reported (Fully healthy, unrestricted movement capacity)"
    )
    notes_str = (
        profile.additional_notes.strip()
        if profile.additional_notes and profile.additional_notes.strip()
        else "Standard programming"
    )

    variation_clause = ""
    if variation_seed is not None:
        variation_clause = f"\n[Variation Seed #{variation_seed}]: Produce an alternative exercise selection and split arrangement while strictly honoring all constraints.\n"

    return f"""Please generate a complete, structured weekly workout program for the following athlete profile:

TRAINEE SPECIFICATIONS:
- Primary Fitness Goal: {profile.fitness_goal}
- Experience Level: {profile.experience_level}
- Training Frequency: {profile.days_per_week} days per week
- Equipment Access: {equipment_str}
- Target Session Duration: {profile.session_duration_minutes} minutes
- Split Preference: {profile.split_preference or "Trainer Optimized Split"}
- Musculoskeletal Limitations / Injuries: {limitations_str}
- Additional Preferences / Focus Areas: {notes_str}
{variation_clause}
---

REQUIRED RESPONSE STRUCTURE:

## 1. Program Overview and Strategy
- Split Summary: Biomechanical rationale for the split choice relative to {profile.days_per_week} days per week and the {profile.fitness_goal} objective.
- Weekly Schedule Matrix: Concise weekly schedule table (e.g., Day 1 to Day 7 training and recovery layout).
- Session Duration Check: Confirmation of volume fitting the ~{profile.session_duration_minutes} minute target.

## 2. Day-by-Day Detailed Workout Plan
For EACH of the {profile.days_per_week} training days, provide:
### Day [X]: [Session Focus and Split Component]
- Dynamic Warm-Up (3 to 5 minutes): 3 specific activation and mobility drills.
- Main Resistance Workout:
  | Exercise Name | Target Muscle | Sets | Reps | Rest | RPE (1-10) | Form Cue |
  |---|---|---|---|---|---|---|
  (Provide 4 to 6 exercises compatible with {equipment_str} and safe for {limitations_str})
- Cool-Down and Mobility (2 to 3 minutes): Targeted post-workout stretches.

(For remaining non-training days, specify Active Recovery or Rest protocols).

## 3. Progressive Overload and Coaching Guidelines
- Progression Protocol: Step-by-step guidance on how to increase load, reps, or tempo across weeks 1 to 4.
- Recovery Recommendations: Hydration, sleep, and recovery principles matched to the {profile.experience_level} level.

## 4. Safety Adaptations and Medical Disclaimer
- Biomechanical Modifications: Explicit explanation of how exercise selection was modified to protect: "{limitations_str}".
- Medical Disclaimer: Clear statement that this program is educational and requires clearance from a licensed physician or physical therapist prior to execution.
"""


def build_exercise_swap_prompt(
    original_exercise: str,
    reason: str,
    profile: UserProfile
) -> str:
    """
    Constructs a prompt to generate 2 to 3 targeted biomechanical substitutions for an exercise.
    """
    equipment_str = ", ".join(profile.equipment_access)
    limitations_str = (
        profile.injuries_or_limitations.strip()
        if profile.injuries_or_limitations and profile.injuries_or_limitations.strip()
        else "None"
    )

    return f"""The user requires an alternative substitution for a specific exercise in their workout program.
Generate 2 to 3 equivalent, joint-safe replacement exercises matching their exact constraints.

SUBSTITUTION PARAMETERS:
- Exercise to Replace: {original_exercise}
- Reason for Substitution: {reason}
- Primary Fitness Goal: {profile.fitness_goal}
- Experience Level: {profile.experience_level}
- Available Equipment: {equipment_str} (STRICT REQUIREMENT: Use ONLY this equipment)
- Joint / Injury Restrictions: {limitations_str} (STRICT REQUIREMENT: Must not irritate this region)

OUTPUT FORMAT:
For each alternative option:
1. Alternative Exercise Name and Equipment Required
2. Biomechanical Justification (movement plane and targeted musculature match)
3. Prescribed Sets, Reps, and Rest Interval
4. Key Form and Execution Cue
"""
