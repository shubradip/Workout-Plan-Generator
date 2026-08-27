"""
Exercise swapping module (Stretch Goal).
Allows users to replace individual exercises with safe, tailored alternatives.
"""

import os
from typing import Optional
from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError
from dotenv import load_dotenv

from .models import UserProfile, SwapResult
from .prompts import SYSTEM_PROMPT, build_exercise_swap_prompt

load_dotenv()


def swap_single_exercise(
    original_exercise: str,
    reason: str,
    profile: UserProfile,
    api_key: Optional[str] = None,
    model: str = "llama-3.3-70b-versatile",
) -> SwapResult:
    """
    Generates tailored alternative exercises for a specific movement based on
    the user's equipment and limitations.

    Args:
        original_exercise (str): Name of exercise to replace.
        reason (str): Reason for swap (e.g. 'shoulder pain', 'equipment unavailable').
        profile (UserProfile): User profile with constraints.
        api_key (Optional[str]): Groq API key.
        model (str): Model name.

    Returns:
        SwapResult: Result containing the markdown alternatives or error message.
    """
    if not original_exercise or not original_exercise.strip():
        return SwapResult(
            success=False,
            error_message="Please specify the exercise name you want to swap.",
        )

    resolved_api_key = (api_key or "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
    if not resolved_api_key:
        return SwapResult(
            success=False,
            error_message="Groq API key is missing. Please provide your API key in the sidebar.",
        )

    prompt = build_exercise_swap_prompt(
        original_exercise=original_exercise.strip(),
        reason=reason.strip() if reason else "Looking for a variation",
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
                error_message="Empty response received for exercise swap.",
            )

        content = response.choices[0].message.content
        return SwapResult(
            success=True,
            replacement_markdown=content.strip() if content else None,
        )

    except AuthenticationError:
        return SwapResult(
            success=False,
            error_message="Authentication failed: Invalid Groq API key.",
        )
    except RateLimitError:
        return SwapResult(
            success=False,
            error_message="Rate limit reached. Please wait a few seconds and try again.",
        )
    except APIConnectionError:
        return SwapResult(
            success=False,
            error_message="Network connection error. Please check your internet.",
        )
    except Exception as e:
        return SwapResult(
            success=False,
            error_message=f"Error swapping exercise: {str(e)}",
        )
