"""
Comprehensive unit tests for Workout Plan Generator.
Tests data models, prompt construction, API handling, and error recovery.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from workout_generator.models import UserProfile, GenerationResult, SwapResult, PRESETS
from workout_generator.prompts import SYSTEM_PROMPT, build_workout_prompt, build_exercise_swap_prompt
from workout_generator.generator import generate_workout_plan
from workout_generator.exercise_swap import swap_single_exercise
from groq import AuthenticationError, RateLimitError, APIConnectionError


class TestUserProfileModel(unittest.TestCase):
    """Tests for UserProfile validation and properties."""

    def test_valid_profile_creation(self):
        profile = UserProfile(
            fitness_goal="Build muscle (Hypertrophy)",
            experience_level="Intermediate",
            days_per_week=4,
            equipment_access=["Home dumbbells & resistance bands"],
            session_duration_minutes=45,
            split_preference="Upper / Lower Split",
            injuries_or_limitations="Bad knees",
            additional_notes="None"
        )
        self.assertEqual(profile.days_per_week, 4)
        self.assertTrue(profile.has_limitations())

    def test_invalid_days_per_week_zero(self):
        with self.assertRaises(ValidationError):
            UserProfile(
                fitness_goal="Lose fat",
                experience_level="Beginner",
                days_per_week=0,  # Invalid: must be >= 1
                equipment_access=["No equipment"],
            )

    def test_invalid_days_per_week_over_seven(self):
        with self.assertRaises(ValidationError):
            UserProfile(
                fitness_goal="Lose fat",
                experience_level="Beginner",
                days_per_week=8,  # Invalid: must be <= 7
                equipment_access=["No equipment"],
            )

    def test_empty_equipment_list(self):
        with self.assertRaises(ValidationError):
            UserProfile(
                fitness_goal="Lose fat",
                experience_level="Beginner",
                days_per_week=3,
                equipment_access=[],  # Invalid: min_length=1
            )

    def test_presets_validity(self):
        """Ensure all built-in presets instantiate cleanly."""
        self.assertGreater(len(PRESETS), 0)
        for name, preset in PRESETS.items():
            self.assertIsInstance(preset, UserProfile)
            self.assertGreaterEqual(preset.days_per_week, 1)
            self.assertLessEqual(preset.days_per_week, 7)
            self.assertTrue(len(preset.equipment_access) > 0)


class TestPromptEngineering(unittest.TestCase):
    """Tests for prompt assembly and constraint propagation."""

    def setUp(self):
        self.profile = UserProfile(
            fitness_goal="Lose fat & tone",
            experience_level="Beginner",
            days_per_week=3,
            equipment_access=["Home dumbbells & resistance bands"],
            session_duration_minutes=30,
            split_preference="Full Body",
            injuries_or_limitations="Shoulder impingement; avoid heavy overhead pressing",
            additional_notes="Prefer core focus"
        )

    def test_system_prompt_integrity(self):
        self.assertIn("CSCS", SYSTEM_PROMPT)
        self.assertIn("EQUIPMENT COMPLIANCE", SYSTEM_PROMPT)
        self.assertIn("INJURIES & LIMITATIONS", SYSTEM_PROMPT)
        self.assertIn("Medical Disclaimer", SYSTEM_PROMPT)

    def test_workout_prompt_contains_all_constraints(self):
        prompt = build_workout_prompt(self.profile)
        self.assertIn("Lose fat & tone", prompt)
        self.assertIn("Beginner", prompt)
        self.assertIn("3 days per week", prompt)
        self.assertIn("Home dumbbells & resistance bands", prompt)
        self.assertIn("30 minutes per workout", prompt)
        self.assertIn("Shoulder impingement; avoid heavy overhead pressing", prompt)
        self.assertIn("Prefer core focus", prompt)
        self.assertIn("Medical Disclaimer", prompt)

    def test_workout_prompt_with_variation_seed(self):
        prompt = build_workout_prompt(self.profile, variation_seed=2)
        self.assertIn("variation #2", prompt)

    def test_exercise_swap_prompt_construction(self):
        prompt = build_exercise_swap_prompt(
            original_exercise="Barbell Overhead Press",
            reason="Sharp shoulder pinch",
            profile=self.profile
        )
        self.assertIn("Barbell Overhead Press", prompt)
        self.assertIn("Sharp shoulder pinch", prompt)
        self.assertIn("Home dumbbells & resistance bands", prompt)


class TestGeneratorFunction(unittest.TestCase):
    """Tests for generate_workout_plan type hints, error handling, and API integration."""

    def setUp(self):
        self.profile = UserProfile(
            fitness_goal="Build muscle (Hypertrophy)",
            experience_level="Intermediate",
            days_per_week=4,
            equipment_access=["Full gym (Barbells, dumbbells, cables, machines)"],
        )

    def test_missing_api_key_returns_friendly_error(self):
        with patch.dict(os.environ, {}, clear=True):
            result = generate_workout_plan(
                profile=self.profile,
                api_key="",
            )
            self.assertFalse(result.success)
            self.assertIn("Groq API key is missing", result.error_message)

    def test_invalid_profile_type(self):
        result = generate_workout_plan(
            profile="not_a_user_profile",  # type: ignore
            api_key="gsk_test123",
        )
        self.assertFalse(result.success)
        self.assertIn("Invalid input", result.error_message)

    @patch("workout_generator.generator.Groq")
    def test_successful_plan_generation(self, mock_groq_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "## 1. 📋 Program Overview\nGreat workout plan details..."
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        result = generate_workout_plan(
            profile=self.profile,
            api_key="gsk_dummy_valid_key",
            model="llama-3.3-70b-versatile",
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.plan_markdown)
        self.assertIn("Program Overview", result.plan_markdown)
        self.assertEqual(result.model_used, "llama-3.3-70b-versatile")
        self.assertGreaterEqual(result.generation_time_sec, 0)

    @patch("workout_generator.generator.Groq")
    def test_authentication_error_handling(self, mock_groq_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_client.chat.completions.create.side_effect = AuthenticationError(
            message="Invalid API Key",
            response=mock_response,
            body={"error": "invalid_api_key"}
        )
        mock_groq_class.return_value = mock_client

        result = generate_workout_plan(
            profile=self.profile,
            api_key="gsk_invalid_key",
        )

        self.assertFalse(result.success)
        self.assertIn("Authentication Error", result.error_message)

    @patch("workout_generator.generator.Groq")
    def test_rate_limit_error_handling(self, mock_groq_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_client.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit exceeded",
            response=mock_response,
            body={"error": "rate_limit_exceeded"}
        )
        mock_groq_class.return_value = mock_client

        result = generate_workout_plan(
            profile=self.profile,
            api_key="gsk_test_key",
        )

        self.assertFalse(result.success)
        self.assertIn("Rate Limit Exceeded", result.error_message)

    @patch("workout_generator.generator.Groq")
    def test_empty_llm_response_handling(self, mock_groq_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "   "  # Empty string
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        result = generate_workout_plan(
            profile=self.profile,
            api_key="gsk_test_key",
        )

        self.assertFalse(result.success)
        self.assertIn("empty response", result.error_message)


class TestExerciseSwapFunction(unittest.TestCase):
    """Tests for swap_single_exercise function."""

    def setUp(self):
        self.profile = UserProfile(
            fitness_goal="Build muscle (Hypertrophy)",
            experience_level="Intermediate",
            days_per_week=4,
            equipment_access=["Home dumbbells & resistance bands"],
        )

    def test_empty_exercise_name(self):
        result = swap_single_exercise(
            original_exercise="",
            reason="shoulder pain",
            profile=self.profile,
            api_key="gsk_test_key"
        )
        self.assertFalse(result.success)
        self.assertIn("specify the exercise name", result.error_message)

    @patch("workout_generator.exercise_swap.Groq")
    def test_successful_swap(self, mock_groq_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "1. **Dumbbell Floor Press**\nSafe on shoulders..."
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        result = swap_single_exercise(
            original_exercise="Barbell Bench Press",
            reason="Shoulder impingement",
            profile=self.profile,
            api_key="gsk_test_key"
        )

        self.assertTrue(result.success)
        self.assertIn("Dumbbell Floor Press", result.replacement_markdown)


if __name__ == "__main__":
    unittest.main()
