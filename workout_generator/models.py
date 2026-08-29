"""
Data models, validation rules, and schema definitions for the Workout Plan Generator.
Authored by Shubradip.

This module enforces strict type boundaries and runtime input validation using Pydantic v2.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    """
    Structured domain model representing a trainee's fitness profile,
    biometric constraints, training frequency, and equipment availability.
    """
    fitness_goal: str = Field(
        ...,
        description="Primary training objective (e.g., Hypertrophy, Fat Loss, Endurance, General Strength)"
    )
    experience_level: str = Field(
        ...,
        description="Training background (Beginner, Intermediate, Advanced)"
    )
    days_per_week: int = Field(
        ...,
        ge=1,
        le=7,
        description="Weekly training frequency (1 to 7 days)"
    )
    equipment_access: List[str] = Field(
        ...,
        min_length=1,
        description="Available training equipment"
    )
    session_duration_minutes: int = Field(
        default=45,
        ge=15,
        le=120,
        description="Target workout duration in minutes"
    )
    split_preference: Optional[str] = Field(
        default="Trainer Optimized Split",
        description="Preferred periodization split structure"
    )
    injuries_or_limitations: Optional[str] = Field(
        default=None,
        description="Reported musculoskeletal limitations, joint pain, or movement restrictions"
    )
    additional_notes: Optional[str] = Field(
        default=None,
        description="Specific muscle group priorities or stylistic preferences"
    )

    @field_validator("days_per_week")
    @classmethod
    def validate_frequency(cls, v: int) -> int:
        if not (1 <= v <= 7):
            raise ValueError("Training frequency must be strictly between 1 and 7 days per week.")
        return v

    @field_validator("equipment_access")
    @classmethod
    def validate_equipment_selection(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one equipment category must be selected.")
        return v

    def has_limitations(self) -> bool:
        """Determines if the user has documented any physical limitations or injuries."""
        return bool(self.injuries_or_limitations and self.injuries_or_limitations.strip())


class GenerationResult(BaseModel):
    """Encapsulates the output of a workout generation request."""
    success: bool
    plan_markdown: Optional[str] = None
    error_message: Optional[str] = None
    model_used: Optional[str] = None
    generation_time_sec: Optional[float] = None


class SwapResult(BaseModel):
    """Encapsulates the response from a targeted exercise substitution request."""
    success: bool
    replacement_markdown: Optional[str] = None
    error_message: Optional[str] = None


# Evaluation presets for rapid testing and benchmarking
PRESETS = {
    "Busy Professional (Home Dumbbells, 3 Days)": UserProfile(
        fitness_goal="Lose Fat and Lean Conditioning",
        experience_level="Beginner",
        days_per_week=3,
        equipment_access=["Home Dumbbells and Resistance Bands"],
        session_duration_minutes=35,
        split_preference="Full Body",
        injuries_or_limitations="Tight lower back from desk posture; avoid direct heavy axial spinal compression",
        additional_notes="Focus on core stability and high metabolic density with controlled rest periods"
    ),
    "Hypertrophy Focus (Full Gym, 5 Days)": UserProfile(
        fitness_goal="Build Muscle (Hypertrophy)",
        experience_level="Intermediate",
        days_per_week=5,
        equipment_access=["Full Commercial Gym (Barbells, Dumbbells, Cables, Machines)"],
        session_duration_minutes=60,
        split_preference="Push / Pull / Legs / Upper / Lower",
        injuries_or_limitations="",
        additional_notes="Target chest and upper back hypertrophy with progressive mechanical tension"
    ),
    "Endurance and Joint Care (Bodyweight, 4 Days)": UserProfile(
        fitness_goal="Improve Endurance and Conditioning",
        experience_level="Intermediate",
        days_per_week=4,
        equipment_access=["Bodyweight Calisthenics Only"],
        session_duration_minutes=45,
        split_preference="Upper / Lower Split",
        injuries_or_limitations="Patellar tendonitis; eliminate deep unassisted lunges and high-impact jumping squats",
        additional_notes="Incorporate low-impact cardiovascular intervals and joint-friendly posterior chain activation"
    ),
    "Strength and Power (Full Gym, 4 Days)": UserProfile(
        fitness_goal="Strength and Power Development",
        experience_level="Advanced",
        days_per_week=4,
        equipment_access=["Full Commercial Gym (Barbells, Dumbbells, Cables, Machines)"],
        session_duration_minutes=75,
        split_preference="Upper / Lower Split",
        injuries_or_limitations="Mild anterior shoulder impingement during standard barbell bench press",
        additional_notes="Emphasize neutral-grip dumbbell pressing and floor presses for pressing volume"
    ),
}
