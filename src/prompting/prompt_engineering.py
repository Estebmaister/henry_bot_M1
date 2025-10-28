"""
Prompt Engineering Module

This module implements prompt engineering techniques to improve the quality
of LLM responses. Uses few-shot prompting to guide the model's output format.
"""

from pathlib import Path
from typing import List, Dict


class PromptBuilder:
    """Builds engineered prompts using simple, few-shot and chain-of-thought techniques."""

    def __init__(self):
        """Initialize the prompt builder with system instructions."""
        prompt_path = Path(__file__).with_name("system_prompt.txt")
        self.system_prompt = prompt_path.read_text(encoding="utf-8").strip()

    def build_few_shot_prompt(self, user_question: str) -> List[Dict[str, str]]:
        """
        Build a few-shot prompt with examples to guide the model.

        Few-shot prompting is a technique where we provide the model with
        examples of the desired input-output format to improve consistency
        and quality of responses.

        Args:
            user_question: The user's question to answer

        Returns:
            List of message dictionaries formatted for the OpenRouter API
        """
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": "What is the capital of France?"
            },
            {
                "role": "assistant",
                "content": '{"answer": "Paris"}'
            },
            {
                "role": "user",
                "content": "What is 2 + 2?"
            },
            {
                "role": "assistant",
                "content": '{"answer": "4"}'
            },
            {
                "role": "user",
                "content": "Who wrote Romeo and Juliet?"
            },
            {
                "role": "assistant",
                "content": '{"answer": "William Shakespeare"}'
            },
            {
                "role": "user",
                "content": user_question
            }
        ]

        return messages

    def build_simple_prompt(self, user_question: str) -> List[Dict[str, str]]:
        """
        Build a simple prompt without examples.

        Args:
            user_question: The user's question to answer

        Returns:
            List of message dictionaries formatted for the OpenRouter API
        """
        messages = [
            {
                "role": "system",
                "content": self.system_prompt + "\nRespond with JSON in this format: {\"answer\": \"your answer here\"}"
            },
            {
                "role": "user",
                "content": user_question
            }
        ]

        return messages

    def build_chain_of_thought_prompt(self, user_question: str) -> List[Dict[str, str]]:
        """
        Build a chain-of-thought prompt for complex reasoning.

        This technique encourages the model to show its reasoning process
        before providing the final answer.

        Args:
            user_question: The user's question to answer

        Returns:
            List of message dictionaries formatted for the OpenRouter API
        """
        enhanced_system_prompt = self.system_prompt + """

When answering complex questions, break down your reasoning step by step.
Always provide your final answer in JSON format: {"answer": "your answer", "reasoning": "brief explanation"}"""

        messages = [
            {
                "role": "system",
                "content": enhanced_system_prompt
            },
            {
                "role": "user",
                "content": user_question
            }
        ]

        return messages


def create_prompt(user_question: str, technique: str = "few_shot") -> List[Dict[str, str]]:
    """
    Convenience function to create a prompt using specified technique.

    Args:
        user_question: The user's question
        technique: Prompting technique to use ('few_shot', 'simple', or 'chain_of_thought')

    Returns:
        List of formatted messages for the API
    """
    builder = PromptBuilder()

    if technique == "few_shot":
        return builder.build_few_shot_prompt(user_question)
    elif technique == "simple":
        return builder.build_simple_prompt(user_question)
    elif technique == "chain_of_thought":
        return builder.build_chain_of_thought_prompt(user_question)
    else:
        # Default to few_shot
        return builder.build_few_shot_prompt(user_question)
