"""
Core LLM generation module interfacing with the Groq inference engine.
Authored by Shubradip.

Implements type-annotated API interaction, parameter validation, and robust
exception handling for authentication, rate limits, and network anomalies.
"""

import os
import time
from typing import Optional
from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError
from dotenv import load_dotenv

from .models import UserProfile, GenerationResult
from .prompts import SYSTEM_PROMPT, build_workout_prompt

# Load environment configuration
load_dotenv()

# Active Groq Model Endpoints
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
    Generates a structured weekly workout program using Groq LLM inference.

    Args:
        profile (UserProfile): Validated user profile model containing goals and constraints.
        api_key (Optional[str]): Groq API key override. Defaults to GROQ_API_KEY environment variable.
        model (str): Target LLM model identifier.
        temperature (float): Sampling temperature between 0.0 and 1.0.
        variation_seed (Optional[int]): Optional integer seed for generating alternate variations.

    Returns:
        GenerationResult: Container containing generation status, markdown content, or error detail.
    """
    start_time = time.time()

    # 1. Validate domain profile
    if not isinstance(profile, UserProfile):
        return GenerationResult(
            success=False,
            error_message="Invalid input: Expected a valid UserProfile instance.",
        )

    if profile.days_per_week < 1 or profile.days_per_week > 7:
        return GenerationResult(
            success=False,
            error_message="Invalid frequency: Weekly workout days must be between 1 and 7.",
        )

    if not profile.equipment_access:
        return GenerationResult(
            success=False,
            error_message="Missing equipment selection: At least one equipment option must be selected.",
        )

    # 2. Resolve authentication credentials
    resolved_api_key = (api_key or "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
    if not resolved_api_key:
        return GenerationResult(
            success=False,
            error_message=(
                "Groq API key not detected. Please provide your API key in the sidebar configuration "
                "or set GROQ_API_KEY in your .env file."
            ),
        )

    # 3. Assemble prompt
    user_prompt = build_workout_prompt(profile, variation_seed=variation_seed)

    # 4. Invoke Groq API client with structured error boundaries
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

        # 5. Validate response structure
        if not response or not response.choices:
            return GenerationResult(
                success=False,
                error_message="Received an empty response payload from the inference endpoint.",
            )

        content = response.choices[0].message.content
        if not content or not content.strip():
            return GenerationResult(
                success=False,
                error_message="The model generated an empty text response. Please trigger a regeneration.",
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
            error_message="Authentication Error: The provided Groq API key is invalid or unauthorized.",
        )

    except RateLimitError as e:
        return GenerationResult(
            success=False,
            error_message=f"Rate Limit Exceeded: Groq API request threshold reached ({str(e)}). Please retry shortly.",
        )

    except APIConnectionError as e:
        return GenerationResult(
            success=False,
            error_message=f"Connection Error: Unable to reach the Groq API endpoint ({str(e)}). Check network connectivity.",
        )

    except APIStatusError as e:
        return GenerationResult(
            success=False,
            error_message=f"API Status Error (Code {e.status_code}): {e.message}",
        )

    except Exception as e:
        return GenerationResult(
            success=False,
            error_message=f"Unexpected Error occurred during plan generation: {str(e)}",
        )
