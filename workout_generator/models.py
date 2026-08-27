"""
Data models and schemas for the Workout Plan Generator.
Includes validation rules and typed representations of user profiles and API results.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    """
    Structured user inputs representing a user's fitness profile,
    goals, constraints, and preferences.
    """
    fitness_goal: str = Field(
        ...,
        description="Primary fitness objective (e.g., Build muscle, Lose fat, General fitness, Improve endurance, Strength & Power)"
    )
    experience_level: str = Field(
        ...,
        description="User training experience (e.g., Beginner, Intermediate, Advanced)"
    )
    days_per_week: int = Field(
        ...,
        ge=1,
        le=7,
        description="Number of workout days available per week (1-7)"
    )
    equipment_access: List[str] = Field(
        ...,
        min_length=1,
        description="Available equipment (e.g., No equipment, Home dumbbells, Full gym)"
    )
    session_duration_minutes: int = Field(
        default=45,
        ge=15,
        le=120,
        description="Target duration per workout session in minutes"
    )
    split_preference: Optional[str] = Field(
        default="Trainer's Choice (Optimized)",
        description="Preferred workout split type"
    )
    injuries_or_limitations: Optional[str] = Field(
        default=None,
        description="Any reported injuries, pain points, or physical limitations"
    )
    additional_notes: Optional[str] = Field(
        default=None,
        description="Additional preferences or focus muscle groups"
    )

    @field_validator("days_per_week")
    @classmethod
    def validate_days(cls, v: int) -> int:
        if not (1 <= v <= 7):
            raise ValueError("Days available per week must be between 1 and 7.")
        return v

    @field_validator("equipment_access")
    @classmethod
    def validate_equipment(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Please select at least one equipment option.")
        return v

    def has_limitations(self) -> bool:
        """Check if user specified any injury or limitation."""
        return bool(self.injuries_or_limitations and self.injuries_or_limitations.strip())


class GenerationResult(BaseModel):
    """Result container for workout plan generation."""
    success: bool
    plan_markdown: Optional[str] = None
    error_message: Optional[str] = None
    model_used: Optional[str] = None
    generation_time_sec: Optional[float] = None


class SwapResult(BaseModel):
    """Result container for single exercise swap."""
    success: bool
    replacement_markdown: Optional[str] = None
    error_message: Optional[str] = None


# Quick Presets for 1-Click Evaluation
PRESETS = {
    "Busy Professional (Home Dumbbells, 3 Days)": UserProfile(
        fitness_goal="Lose fat & get lean",
        experience_level="Beginner",
        days_per_week=3,
        equipment_access=["Home dumbbells & resistance bands"],
        session_duration_minutes=35,
        split_preference="Full Body",
        injuries_or_limitations="Tight lower back from sitting all day; no heavy spinal loading",
        additional_notes="Focus on core stability and high calorie burn with short rest periods"
    ),
    "Hypertrophy Seeker (Full Gym, 5 Days)": UserProfile(
        fitness_goal="Build muscle (Hypertrophy)",
        experience_level="Intermediate",
        days_per_week=5,
        equipment_access=["Full gym (Barbells, dumbbells, cables, machines)"],
        session_duration_minutes=60,
        split_preference="Push / Pull / Legs / Upper / Lower",
        injuries_or_limitations="",
        additional_notes="Target chest and upper back hypertrophy"
    ),
    "Endurance Athlete & Joint Care (Bodyweight, 4 Days)": UserProfile(
        fitness_goal="Improve endurance & conditioning",
        experience_level="Intermediate",
        days_per_week=4,
        equipment_access=["No equipment (Bodyweight only)"],
        session_duration_minutes=45,
        split_preference="Upper / Lower Split",
        injuries_or_limitations="Patellar tendonitis (bad knees); avoid deep unassisted lunges or jumping squats",
        additional_notes="Include low-impact cardiovascular conditioning and knee-friendly glute activation"
    ),
    "Strength & Power (Full Gym, 4 Days)": UserProfile(
        fitness_goal="Strength & Power",
        experience_level="Advanced",
        days_per_week=4,
        equipment_access=["Full gym (Barbells, dumbbells, cables, machines)"],
        session_duration_minutes=75,
        split_preference="Upper / Lower Split",
        injuries_or_limitations="Mild shoulder impingement on flat bench press",
        additional_notes="Prefer neutral grip pressing or slight incline; focus on compound lifts"
    ),
}
