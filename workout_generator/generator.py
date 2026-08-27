"""
Core generation module interfacing with the Groq API.
Includes comprehensive type hints, input validation, and detailed exception handling.
"""

import os
import time
from typing import Optional
from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError
from dotenv import load_dotenv

from .models import UserProfile, GenerationResult
from .prompts import SYSTEM_PROMPT, build_workout_prompt

# Load environment variables from .env if present
load_dotenv()

# Supported Groq Models
DEFAULT_MODEL = "qwen/qwen3.8-27b"
AVAILABLE_MODELS = [
    "qwen/qwen3.8-27b",
    "qwen/qwen3.6-27b",
    "groq/compound",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]


def generate_workout_plan(
    profile: UserProfile,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.5,
    variation_seed: Optional[int] = None,
) -> GenerationResult:
    """
    Generates a structured weekly workout plan using the Groq LLM API.

    Args:
        profile (UserProfile): The structured user profile and constraints.
        api_key (Optional[str]): Groq API key. If not provided, reads from GROQ_API_KEY env var.
        model (str): Groq model identifier (e.g. 'llama-3.3-70b-versatile').
        temperature (float): Sampling temperature (0.0 to 1.0) for generation variety.
        variation_seed (Optional[int]): Optional seed index to produce fresh variations.

    Returns:
        GenerationResult: Object containing success status, markdown plan, or friendly error message.
    """
    start_time = time.time()

    # 1. Validate structured input
    if not isinstance(profile, UserProfile):
        return GenerationResult(
            success=False,
            error_message="Invalid input: Expected a UserProfile instance.",
        )

    if profile.days_per_week < 1 or profile.days_per_week > 7:
        return GenerationResult(
            success=False,
            error_message="Invalid days per week: Training days must be between 1 and 7.",
        )

    if not profile.equipment_access:
        return GenerationResult(
            success=False,
            error_message="Missing equipment: Please select at least one equipment option.",
        )

    # 2. Resolve Groq API Key
    resolved_api_key = (api_key or "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
    if not resolved_api_key:
        return GenerationResult(
            success=False,
            error_message=(
                "🔑 Groq API key is missing!\n\n"
                "Please enter your Groq API key in the sidebar, or add `GROQ_API_KEY=gsk_...` "
                "to your `.env` file.\n\n"
                "You can get a free API key at [console.groq.com/keys](https://console.groq.com/keys)."
            ),
        )

    # 3. Construct prompt
    user_prompt = build_workout_prompt(profile, variation_seed=variation_seed)

    # 4. Call Groq API with robust exception handling
    try:
        client = Groq(api_key=resolved_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=4096,
        )

        # 5. Validate response content
        if not response or not response.choices:
            return GenerationResult(
                success=False,
                error_message="Received an empty response from Groq API. Please try again.",
            )

        content = response.choices[0].message.content
        if not content or not content.strip():
            return GenerationResult(
                success=False,
                error_message="The model generated an empty response. Please try regenerating the plan.",
            )

        elapsed = round(time.time() - start_time, 2)
        return GenerationResult(
            success=True,
            plan_markdown=content.strip(),
            model_used=model,
            generation_time_sec=elapsed,
        )

    except AuthenticationError:
        return GenerationResult(
            success=False,
            error_message=(
                "❌ Authentication Error: The provided Groq API key is invalid or expired. "
                "Please verify your key in the sidebar."
            ),
        )

    except RateLimitError as e:
        return GenerationResult(
            success=False,
            error_message=(
                f"⏱️ Rate Limit Exceeded: Groq API rate limit reached ({str(e)}). "
                "Please wait a few moments before trying again or switch to a faster model like `llama-3.1-8b-instant`."
            ),
        )

    except APIConnectionError as e:
        return GenerationResult(
            success=False,
            error_message=(
                f"🌐 Network Connection Error: Unable to reach the Groq API servers ({str(e)}). "
                "Please check your internet connection and try again."
            ),
        )

    except APIStatusError as e:
        return GenerationResult(
            success=False,
            error_message=f"⚠️ Groq API returned status code {e.status_code}: {e.message}",
        )

    except Exception as e:
        return GenerationResult(
            success=False,
            error_message=f"⚠️ An unexpected error occurred while generating the plan: {str(e)}",
        )
