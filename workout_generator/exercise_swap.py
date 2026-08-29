"""
Exercise substitution module.
Authored by Shubradip.

Provides targeted LLM-driven exercise replacement based on biomechanical
equivalents and user physical constraints.
"""

import os
from typing import Optional
from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError
from dotenv import load_dotenv

from .models import UserProfile, SwapResult
from .prompts import SYSTEM_PROMPT, build_exercise_swap_prompt

load_dotenv()


def swap_single_exercise(
    original_exercise: str,
    reason: str,
    profile: UserProfile,
    api_key: Optional[str] = None,
    model: str = "qwen/qwen3.8-27b",
) -> SwapResult:
    """
    Generates targeted biomechanical replacements for a specific exercise movement.

    Args:
        original_exercise (str): Name of the exercise to substitute.
        reason (str): Context or reason for substitution.
        profile (UserProfile): Trainee constraints and equipment access.
        api_key (Optional[str]): Groq API key override.
        model (str): Target LLM model identifier.

    Returns:
        SwapResult: Data container with formatted alternative exercises or error messages.
    """
    if not original_exercise or not original_exercise.strip():
        return SwapResult(
            success=False,
            error_message="Please specify the exercise name to substitute.",
        )

    resolved_api_key = (api_key or "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
    if not resolved_api_key:
        return SwapResult(
            success=False,
            error_message="Groq API key not found. Please provide an API key in the sidebar.",
        )

    prompt = build_exercise_swap_prompt(
        original_exercise=original_exercise.strip(),
        reason=reason.strip() if reason else "General variation request",
        profile=profile,
    )

    try:
        client = Groq(api_key=resolved_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=1500,
        )

        if not response or not response.choices:
            return SwapResult(
                success=False,
                error_message="Empty response received for exercise substitution.",
            )

        content = response.choices[0].message.content
        return SwapResult(
            success=True,
            replacement_markdown=content.strip() if content else None,
        )

    except AuthenticationError:
        return SwapResult(
            success=False,
            error_message="Authentication failed: Invalid Groq API key provided.",
        )
    except RateLimitError:
        return SwapResult(
            success=False,
            error_message="Rate limit reached. Please wait a moment before trying again.",
        )
    except APIConnectionError:
        return SwapResult(
            success=False,
            error_message="Network connection error. Unable to communicate with Groq servers.",
        )
    except Exception as e:
        return SwapResult(
            success=False,
            error_message=f"Error performing exercise substitution: {str(e)}",
        )
