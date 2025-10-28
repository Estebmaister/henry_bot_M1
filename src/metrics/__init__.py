"""
Metrics Tracking Module

This module tracks and calculates key performance metrics for LLM API calls:
- Latency (response time in milliseconds)
- Token usage (input + output tokens)
- Estimated API cost in USD

Pricing is based on OpenRouter's model pricing.
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelPricing:
    """Pricing information for LLM models."""
    prompt_price_per_1k: float  # Cost per 1K prompt tokens
    completion_price_per_1k: float  # Cost per 1K completion tokens


# Common model pricing (in USD per 1K tokens)
# These are approximate rates for OpenRouter
MODEL_PRICING = {
    "openai/gpt-3.5-turbo": ModelPricing(0.0005, 0.0015),
    "openai/gpt-4": ModelPricing(0.03, 0.06),
    "openai/gpt-4-turbo": ModelPricing(0.01, 0.03),
    "anthropic/claude-3-haiku": ModelPricing(0.00025, 0.00125),
    "anthropic/claude-3-sonnet": ModelPricing(0.003, 0.015),
    "anthropic/claude-3-opus": ModelPricing(0.015, 0.075),
    "meta-llama/llama-3-8b": ModelPricing(0.0001, 0.0001),
    # Default pricing for unknown models
    "default": ModelPricing(0.001, 0.002)
}


class MetricsTracker:
    """Tracks metrics for LLM API calls."""

    def __init__(self, model: str = "openai/gpt-3.5-turbo"):
        """
        Initialize the metrics tracker.

        Args:
            model: The model identifier being used
        """
        self.model = model
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0

    def start(self) -> None:
        """Start tracking latency."""
        self.start_time = time.time()

    def stop(self) -> None:
        """Stop tracking latency."""
        self.end_time = time.time()

    def set_token_usage(self, prompt_tokens: int, completion_tokens: int, total_tokens: int) -> None:
        """
        Set token usage from API response.

        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            total_tokens: Total tokens used
        """
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens

    def get_latency_ms(self) -> int:
        """
        Calculate latency in milliseconds.

        Returns:
            Latency in milliseconds (rounded to nearest integer)
        """
        if self.start_time is None or self.end_time is None:
            return 0

        latency_seconds = self.end_time - self.start_time
        return round(latency_seconds * 1000)

    def calculate_cost(self) -> float:
        """
        Calculate estimated API cost in USD.

        Returns:
            Estimated cost in USD (rounded to 5 decimal places)
        """
        # Get pricing for the model or use default
        pricing = MODEL_PRICING.get(self.model, MODEL_PRICING["default"])

        # Calculate costs
        prompt_cost = (self.prompt_tokens / 1000) * pricing.prompt_price_per_1k
        completion_cost = (self.completion_tokens / 1000) * pricing.completion_price_per_1k
        total_cost = prompt_cost + completion_cost

        return round(total_cost, 5)

    def get_metrics(self) -> Dict[str, any]:
        """
        Get all tracked metrics.

        Returns:
            Dictionary containing latency, token usage, and cost
        """
        return {
            "latency_ms": self.get_latency_ms(),
            "tokens_total": self.total_tokens,
            "tokens_prompt": self.prompt_tokens,
            "tokens_completion": self.completion_tokens,
            "cost_usd": self.calculate_cost(),
            "model": self.model
        }

    def get_summary_metrics(self) -> Dict[str, any]:
        """
        Get summary metrics (as shown in README examples).

        Returns:
            Dictionary with key metrics only
        """
        return {
            "latency_ms": self.get_latency_ms(),
            "tokens_total": self.total_tokens,
            "cost_usd": self.calculate_cost()
        }


def track_api_call(model: str = "openai/gpt-3.5-turbo") -> MetricsTracker:
    """
    Create a metrics tracker for an API call.

    Args:
        model: The model identifier being used

    Returns:
        Initialized MetricsTracker instance
    """
    tracker = MetricsTracker(model)
    tracker.start()
    return tracker
