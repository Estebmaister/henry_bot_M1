"""
Logging Module

This module provides comprehensive logging for the Henry Bot application:
- Logs all metrics (latency, token usage, costs) to CSV
- Logs all errors and exceptions to CSV
- Logs adversarial prompt detection events to CSV
- Thread-safe logging operations
- Automatic log file creation and management

CSV files are stored in a 'logs' directory with the following structure:
- logs/metrics.csv: API call metrics
- logs/errors.csv: Error and exception logs
- logs/adversarial.csv: Adversarial prompt detection logs
"""

import csv
import threading
import re
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path


class CSVLogger:
    """Thread-safe CSV logger for metrics, errors, and events."""

    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the CSV logger.

        Args:
            log_dir: Directory to store log files (default: 'logs')
        """
        self.log_dir = Path(log_dir)
        self.lock = threading.Lock()

        # Determine project root for path sanitization
        # Navigate up from the logs directory to find project root
        self.project_root = Path.cwd()

        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Define log file paths
        self.metrics_log = self.log_dir / "metrics.csv"
        self.errors_log = self.log_dir / "errors.csv"
        self.adversarial_log = self.log_dir / "adversarial.csv"

        # Initialize log files with headers if they don't exist
        self._initialize_logs()

    def _initialize_logs(self) -> None:
        """Initialize log files with headers if they don't exist."""
        # Metrics log headers
        if not self.metrics_log.exists():
            self._write_csv_row(
                self.metrics_log,
                [
                    "timestamp",
                    "model",
                    "latency_ms",
                    "tokens_prompt",
                    "tokens_completion",
                    "tokens_total",
                    "cost_usd",
                    "prompt_technique",
                    "success"
                ]
            )

        # Errors log headers
        if not self.errors_log.exists():
            self._write_csv_row(
                self.errors_log,
                [
                    "timestamp",
                    "error_type",
                    "error_message",
                    "model",
                    "user_question",
                    "stack_trace"
                ]
            )

        # Adversarial log headers
        if not self.adversarial_log.exists():
            self._write_csv_row(
                self.adversarial_log,
                [
                    "timestamp",
                    "user_question",
                    "detected_patterns",
                    "pattern_count"
                ]
            )

    def _sanitize_path(self, text: str) -> str:
        """
        Sanitize file paths in text to prevent exposing system information.
        Converts absolute paths to relative paths from project root.

        Args:
            text: Text potentially containing file paths

        Returns:
            Text with absolute paths replaced by relative paths
        """
        # Get the absolute project root path as string
        project_root_str = str(self.project_root)

        # Pattern to match file paths in stack traces
        # Matches quoted paths: File "/absolute/path/to/file.py", line X
        path_pattern = r'File "([^"]+)"'

        def replace_path(match):
            abs_path = match.group(1)

            # Check if path is in venv or external libraries first
            if 'venv' in abs_path or 'site-packages' in abs_path or '/opt/' in abs_path or '/usr/' in abs_path:
                # External library - anonymize it by default
                pass
            # If path starts with project root, make it relative
            elif abs_path.startswith(project_root_str):
                rel_path = abs_path[len(project_root_str):].lstrip('/')
                return f'File "./{rel_path}"'
            # Any other absolute path - anonymize it
            filename = Path(abs_path).name
            return f'File "<external>/{filename}"'

        # Replace all file paths in the text
        sanitized = re.sub(path_pattern, replace_path, text)
        return sanitized

    def _sanitize_field(self, field: Any) -> str:
        """
        Sanitize a field by converting to string, removing newlines, and sanitizing file paths.

        Args:
            field: The field value to sanitize

        Returns:
            Sanitized string with newlines replaced by spaces and paths sanitized
        """
        # Convert to string
        field_str = str(field)
        # Sanitize file paths to prevent exposing system information
        field_str = self._sanitize_path(field_str)
        # Replace newlines with spaces
        field_str = field_str.replace('\n', ' ').replace('\r', ' ')
        # Remove excessive whitespace
        field_str = ' '.join(field_str.split())
        return field_str

    def _write_csv_row(self, file_path: Path, row: list) -> None:
        """
        Thread-safe write of a single row to CSV file.
        Sanitizes all fields to remove newlines.

        Args:
            file_path: Path to the CSV file
            row: List of values to write
        """
        # Sanitize all fields in the row
        sanitized_row = [self._sanitize_field(field) for field in row]

        with self.lock:
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(sanitized_row)

    def log_metrics(
        self,
        model: str,
        latency_ms: int,
        tokens_prompt: int,
        tokens_completion: int,
        tokens_total: int,
        cost_usd: float,
        prompt_technique: str = "few_shot",
        success: bool = True
    ) -> None:
        """
        Log API call metrics to CSV.

        Args:
            model: The LLM model used
            latency_ms: Response latency in milliseconds
            tokens_prompt: Number of prompt tokens
            tokens_completion: Number of completion tokens
            tokens_total: Total tokens used
            cost_usd: Estimated cost in USD
            prompt_technique: Prompting technique used
            success: Whether the API call succeeded
        """
        timestamp = datetime.now().isoformat()

        row = [
            timestamp,
            model,
            latency_ms,
            tokens_prompt,
            tokens_completion,
            tokens_total,
            cost_usd,
            prompt_technique,
            success
        ]

        self._write_csv_row(self.metrics_log, row)

    def log_error(
        self,
        error_type: str,
        error_message: str,
        model: Optional[str] = None,
        user_question: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> None:
        """
        Log an error or exception to CSV.

        Args:
            error_type: Type/class of the error
            error_message: Error message
            model: Model being used (if applicable)
            user_question: User question that caused the error (if applicable)
            stack_trace: Full stack trace (if available)
        """
        timestamp = datetime.now().isoformat()

        row = [
            timestamp,
            error_type,
            error_message,
            model or "N/A",
            user_question or "N/A",
            stack_trace or "N/A"
        ]

        self._write_csv_row(self.errors_log, row)

    def log_adversarial(
        self,
        user_question: str,
        detected_patterns: list,
    ) -> None:
        """
        Log an adversarial prompt detection event to CSV.

        Args:
            user_question: The user's question that triggered detection
            detected_patterns: List of detected adversarial patterns
        """
        timestamp = datetime.now().isoformat()

        # Join patterns into a single string for CSV storage
        patterns_str = " | ".join(detected_patterns)

        row = [
            timestamp,
            user_question,
            patterns_str,
            len(detected_patterns)
        ]

        self._write_csv_row(self.adversarial_log, row)

    def log_metrics_from_tracker(
        self,
        tracker: Any,
        prompt_technique: str = "few_shot",
        success: bool = True
    ) -> None:
        """
        Log metrics from a MetricsTracker instance.

        Args:
            tracker: MetricsTracker instance with metrics data
            prompt_technique: Prompting technique used
            success: Whether the API call succeeded
        """
        self.log_metrics(
            model=tracker.model,
            latency_ms=tracker.get_latency_ms(),
            tokens_prompt=tracker.prompt_tokens,
            tokens_completion=tracker.completion_tokens,
            tokens_total=tracker.total_tokens,
            cost_usd=tracker.calculate_cost(),
            prompt_technique=prompt_technique,
            success=success
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about logged data.

        Returns:
            Dictionary with counts of logged entries
        """
        stats = {
            "metrics_entries": 0,
            "error_entries": 0,
            "adversarial_entries": 0
        }

        # Count lines in each log file (excluding header)
        if self.metrics_log.exists():
            with open(self.metrics_log, 'r') as f:
                stats["metrics_entries"] = sum(1 for _ in f) - 1

        if self.errors_log.exists():
            with open(self.errors_log, 'r') as f:
                stats["error_entries"] = sum(1 for _ in f) - 1

        if self.adversarial_log.exists():
            with open(self.adversarial_log, 'r') as f:
                stats["adversarial_entries"] = sum(1 for _ in f) - 1

        return stats


# Global logger instance (singleton pattern)
_logger_instance: Optional[CSVLogger] = None
_logger_lock = threading.Lock()


def get_logger(log_dir: str = "logs") -> CSVLogger:
    """
    Get or create the global logger instance.

    Args:
        log_dir: Directory to store log files

    Returns:
        Global CSVLogger instance
    """
    global _logger_instance

    if _logger_instance is None:
        with _logger_lock:
            if _logger_instance is None:
                _logger_instance = CSVLogger(log_dir)

    return _logger_instance


# Convenience functions for easy access
def log_metrics(**kwargs) -> None:
    """Log metrics using the global logger."""
    get_logger().log_metrics(**kwargs)


def log_error(**kwargs) -> None:
    """Log error using the global logger."""
    get_logger().log_error(**kwargs)


def log_adversarial(**kwargs) -> None:
    """Log adversarial detection using the global logger."""
    get_logger().log_adversarial(**kwargs)


def log_metrics_from_tracker(tracker: Any, **kwargs) -> None:
    """Log metrics from tracker using the global logger."""
    get_logger().log_metrics_from_tracker(tracker, **kwargs)
