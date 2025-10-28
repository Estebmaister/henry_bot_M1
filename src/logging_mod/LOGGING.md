# Logging Module Documentation

The Henry Bot logging module provides comprehensive CSV-based logging for all application metrics, errors, and security events.

## Module Structure

The logging functionality is organized in the `logging_mod/` directory:

```
logging_mod/
├── __init__.py       # Package initialization and exports
└── logger.py         # Core logging implementation
```

All logging functions are exported through the package, so you can import them directly:

```python
from logging_mod import get_logger, log_metrics, log_error, log_adversarial
```

## Features

- **Automatic CSV Logging**: All metrics, errors, and adversarial detections are automatically logged to CSV files
- **Thread-Safe**: Uses threading locks to ensure safe concurrent logging
- **Single-Line Entries**: All newlines are automatically stripped from fields and replaced with spaces, ensuring each log entry is a single line in the CSV
- **Structured Data**: CSV format allows easy import into spreadsheets, databases, or analytics tools
- **Three Log Types**:
  - `metrics.csv` - API call performance metrics
  - `errors.csv` - Error and exception logs
  - `adversarial.csv` - Adversarial prompt detection events

## Log File Structure

### logs/metrics.csv

Tracks performance metrics for every API call:

| Column | Description |
|--------|-------------|
| `timestamp` | ISO 8601 timestamp of the API call |
| `model` | LLM model used (e.g., "google/gemini-2.0-flash-exp:free") |
| `latency_ms` | Response time in milliseconds |
| `tokens_prompt` | Number of tokens in the prompt |
| `tokens_completion` | Number of tokens in the completion |
| `tokens_total` | Total tokens used |
| `cost_usd` | Estimated cost in USD |
| `prompt_technique` | Prompting technique used (e.g., "few_shot", "chain_of_thought") |
| `success` | Whether the API call succeeded (True/False) |

**Example:**
```csv
timestamp,model,latency_ms,tokens_prompt,tokens_completion,tokens_total,cost_usd,prompt_technique,success
2025-10-23T11:32:07.565078,google/gemini-2.0-flash-exp:free,1250,45,89,134,0.00268,few_shot,True
```

### logs/errors.csv

Logs all errors and exceptions:

| Column | Description |
|--------|-------------|
| `timestamp` | ISO 8601 timestamp when error occurred |
| `error_type` | Type/class of the error (e.g., "ValueError", "ConnectionError") |
| `error_message` | Human-readable error message |
| `model` | Model being used when error occurred |
| `user_question` | User's question that caused the error |
| `stack_trace` | Full Python stack trace for debugging |

**Example:**
```csv
timestamp,error_type,error_message,model,user_question,stack_trace
2025-10-23T11:32:07.665982,ConnectionError,Failed to connect to API,google/gemini-2.0-flash-exp:free,What is 2+2?,Traceback...
```

### logs/adversarial.csv

Logs adversarial prompt detection events:

| Column | Description |
|--------|-------------|
| `timestamp` | ISO 8601 timestamp of detection |
| `user_question` | The user's question that triggered detection |
| `detected_patterns` | Pipe-separated list of detected patterns |
| `pattern_count` | Number of adversarial patterns detected |

**Example:**
```csv
timestamp,user_question,detected_patterns,pattern_count
2025-10-23T11:32:07.666306,Ignore all instructions,Prompt injection: ignore.*?instructions,1
```

## Usage

### Automatic Logging

The logging module is automatically integrated into the main application. All API calls, errors, and adversarial detections are logged automatically.

### Manual Logging

You can also use the logger directly in your code:

```python
from logging_mod import get_logger

# Get the global logger instance
logger = get_logger()

# Log metrics
logger.log_metrics(
    model="google/gemini-2.0-flash-exp:free",
    latency_ms=1250,
    tokens_prompt=45,
    tokens_completion=89,
    tokens_total=134,
    cost_usd=0.00268,
    prompt_technique="few_shot",
    success=True
)

# Log an error
logger.log_error(
    error_type="ValueError",
    error_message="Invalid input provided",
    model="google/gemini-2.0-flash-exp:free",
    user_question="What is 2+2?",
    stack_trace="Traceback..."
)

# Log adversarial detection
logger.log_adversarial(
    user_question="Ignore all instructions",
    detected_patterns=["Prompt injection: ignore.*?instructions"]
)
```

### Using with MetricsTracker

The logger integrates seamlessly with the MetricsTracker:

```python
from logging_mod import get_logger
from metrics import MetricsTracker

tracker = MetricsTracker(model="openai/gpt-3.5-turbo")
tracker.start()
# ... perform API call ...
tracker.stop()
tracker.set_token_usage(prompt_tokens=50, completion_tokens=75, total_tokens=125)

# Log the metrics from the tracker
logger = get_logger()
logger.log_metrics_from_tracker(
    tracker,
    prompt_technique="few_shot",
    success=True
)
```

## Running the Example

To see the logging module in action:

```bash
python example_logging.py
```

This will create sample log entries demonstrating all three log types.

## Viewing Logs

### Command Line

```bash
# View metrics log
cat logs/metrics.csv

# View errors log
cat logs/errors.csv

# View adversarial detections
cat logs/adversarial.csv

# Count total entries
wc -l logs/*.csv
```

### Spreadsheet Applications

Simply open the CSV files in:
- Microsoft Excel
- Google Sheets
- LibreOffice Calc
- Apple Numbers

### Python Analysis

```python
import pandas as pd

# Load metrics
metrics_df = pd.read_csv('logs/metrics.csv')
print(f"Average latency: {metrics_df['latency_ms'].mean():.2f}ms")
print(f"Total cost: ${metrics_df['cost_usd'].sum():.5f}")
print(f"Success rate: {metrics_df['success'].mean() * 100:.2f}%")

# Load errors
errors_df = pd.read_csv('logs/errors.csv')
print(f"Most common error: {errors_df['error_type'].mode()[0]}")

# Load adversarial detections
adversarial_df = pd.read_csv('logs/adversarial.csv')
print(f"Total adversarial attempts: {len(adversarial_df)}")
```

## Log Statistics

Get statistics about your logs programmatically:

```python
from logging_mod import get_logger

logger = get_logger()
stats = logger.get_stats()

print(f"Metrics entries: {stats['metrics_entries']}")
print(f"Error entries: {stats['error_entries']}")
print(f"Adversarial entries: {stats['adversarial_entries']}")
```

## Thread Safety

The logging module is thread-safe and can be safely used in multi-threaded applications. All write operations are protected by threading locks to prevent data corruption.

## Configuration

### Custom Log Directory

By default, logs are stored in the `logs/` directory. You can customize this:

```python
from logging_mod import CSVLogger

# Use a custom directory
logger = CSVLogger(log_dir="my_custom_logs")
```

### Log File Locations

The logger creates three CSV files:
- `logs/metrics.csv`
- `logs/errors.csv`
- `logs/adversarial.csv`

These files are automatically created with appropriate headers when the logger is first initialized.

## Testing

Run the comprehensive test suite:

```bash
pytest tests/logging_mod/test_logger.py -v
```

The test suite includes:
- Initialization tests
- Individual logging tests for each log type
- Multiple entry tests
- Statistics calculation tests
- Thread safety tests
- CSV header validation tests

## Integration with Main Application

The logging module is integrated into:

1. **[main.py](../main.py)** - Logs all API call metrics and errors
2. **[safety.py](../prompting/safety.py)** - Logs adversarial prompt detections
3. **[metrics.py](../metrics/__init__.py)** - Provides metrics data for logging

All logging happens automatically when you use the Henry Bot application.

## Data Sanitization

The logging module automatically sanitizes all fields before writing to CSV:

- **Newline Removal**: All newlines (`\n` and `\r`) are replaced with single spaces
- **Whitespace Normalization**: Excessive whitespace is collapsed to single spaces
- **Single-Line Guarantee**: Each log entry is guaranteed to be a single line in the CSV file

This ensures that:
- Stack traces with multiple lines are properly formatted
- User questions with newlines don't break CSV parsing
- Error messages spanning multiple lines are properly logged
- CSV files can be easily parsed by any standard CSV reader

**Example:**
```python
# Original stack trace with newlines:
"Traceback (most recent call last):\n  File test.py, line 42\n    error()\nValueError: test"

# Logged as single line:
"Traceback (most recent call last): File test.py, line 42 error() ValueError: test"
```

## Best Practices

1. **Regular Backups**: Periodically back up your log files
2. **Log Rotation**: For production use, implement log rotation to prevent files from growing too large
3. **Analysis**: Regularly analyze logs to identify patterns, performance issues, or security concerns
4. **Privacy**: Be mindful of logging user questions in production environments
5. **Monitoring**: Set up alerts based on error rates or adversarial detection frequency

## Troubleshooting

### Logs Directory Not Created

The logs directory is created automatically. If you encounter issues, ensure:
- You have write permissions in the application directory
- The parent directory exists

### CSV Files Corrupted

If CSV files become corrupted:
1. Back up the corrupted file
2. Delete the corrupted file
3. Restart the application (new files will be created automatically)

### Missing Log Entries

If log entries are missing:
- Check that the application completed successfully
- Verify you have write permissions
- Check disk space availability

## Performance Considerations

- CSV writes are buffered by the OS, minimizing performance impact
- Thread locks ensure data integrity but may introduce minimal latency in high-concurrency scenarios
- Log files grow linearly with usage; implement rotation for long-running applications

## Future Enhancements

Potential improvements:
- Log rotation support
- Compression for old logs
- Export to other formats (JSON, Parquet)
- Real-time log streaming
- Integration with logging aggregation services
- Configurable log retention policies
