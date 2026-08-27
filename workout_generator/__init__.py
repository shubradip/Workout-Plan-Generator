"""
Workout Plan Generator package.
"""

from .models import UserProfile, GenerationResult, SwapResult
from .generator import generate_workout_plan
from .exercise_swap import swap_single_exercise

__all__ = [
    "UserProfile",
    "GenerationResult",
    "SwapResult",
    "generate_workout_plan",
    "swap_single_exercise",
]
