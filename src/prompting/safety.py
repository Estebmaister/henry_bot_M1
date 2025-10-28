"""
Adversarial Prompt Detection Module

This module detects and flags potentially malicious or manipulative prompts
that attempt prompt injection, seek sensitive information, or contain
other adversarial patterns.
"""

import re
from typing import Dict, List, Tuple
from logging_mod import log_adversarial


class AdversarialPromptDetector:
    """Detects adversarial patterns in user prompts."""

    def __init__(self):
        """Initialize the detector with adversarial patterns."""
        # Patterns for prompt injection attempts
        self.injection_patterns = [
            r'ignore\s+.*?\binstructions?\b',
            r'forget\s+.*?\binstructions?\b',
            r'disregard\s+.*?\binstructions?\b',
            r'override\s+.*?\binstructions?\b',
            r'new\s+instructions?:',
            r'system\s+prompt',
            r'reveal\s+(your\s+)?(system|instructions?|prompt)',
            r'show\s+(me\s+)?(your\s+)?(system|instructions?|prompt)',
            r'what\s+(are|is)\s+(your\s+)?(system|instructions?|prompt)',
        ]

        # Patterns for sensitive information requests
        self.sensitive_patterns = [
            r'(api|secret|private)\s+key',
            r'password',
            r'credentials?',
            r'access\s+token',
            r'authentication\s+token',
            r'database\s+connection',
            r'env(ironment)?\s+variable',
        ]

        # Patterns for role manipulation
        self.role_manipulation_patterns = [
            r'you\s+are\s+now',
            r'act\s+as\s+(a\s+)?',
            r'pretend\s+(to\s+be|you\s+are)',
            r'simulate\s+(a\s+)?',
            r'roleplay\s+as',
        ]

    def detect(self, user_input: str) -> Tuple[bool, List[str]]:
        """
        Detect adversarial patterns in user input.

        Args:
            user_input: The user's input text to analyze

        Returns:
            Tuple of (is_adversarial, list_of_detected_patterns)
        """
        detected_patterns = []
        user_input_lower = user_input.lower()

        # Check for prompt injection
        for pattern in self.injection_patterns:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                detected_patterns.append(f"Prompt injection: {pattern}")

        # Check for sensitive information requests
        for pattern in self.sensitive_patterns:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                detected_patterns.append(f"Sensitive info request: {pattern}")

        # Check for role manipulation
        for pattern in self.role_manipulation_patterns:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                detected_patterns.append(f"Role manipulation: {pattern}")

        is_adversarial = len(detected_patterns) > 0
        return is_adversarial, detected_patterns

    def get_safe_response(self) -> Dict[str, str]:
        """
        Return a safe error response for adversarial prompts.

        Returns:
            Dictionary with error message
        """
        return {
            "error": "Detected adversarial prompt"
        }


def check_adversarial_prompt(user_input: str) -> Tuple[bool, Dict]:
    """
    Convenience function to check if a prompt is adversarial.

    Args:
        user_input: The user's input text

    Returns:
        Tuple of (is_adversarial, response_dict)
    """
    detector = AdversarialPromptDetector()
    is_adversarial, patterns = detector.detect(user_input)

    if is_adversarial:
        # Log the adversarial detection event to CSV
        log_adversarial(
            user_question=user_input,
            detected_patterns=patterns
        )
        return True, detector.get_safe_response()

    return False, {}
