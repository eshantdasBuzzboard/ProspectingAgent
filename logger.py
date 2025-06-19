import logging
import traceback
import os
import sys
import json


def setup_logger():
    """Setup simple logger that writes to app.log"""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Create formatter with file path, line number, and function name
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(pathname)s:%(lineno)d | %(funcName)s() | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create file handler
    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Create console handler (optional - remove if you don't want console output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Configure logger
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # Clear existing handlers
    logger.addHandler(file_handler)
    logger.addHandler(
        console_handler
    )  # Comment this line if you don't want console output

    return logger


# Create the logger instance
logger = setup_logger()


def info(message):
    """Log info message"""
    logger.info(message)


def debug(message):
    """Log debug message"""
    logger.debug(message)


def warning(message):
    """Log warning message"""
    logger.warning(message)


def error(message):
    """Log error message with traceback if there's an active exception"""
    logger.error(message)
    # If there's an active exception, log the traceback
    if sys.exc_info()[0] is not None:
        logger.error(f"Traceback:\n{traceback.format_exc()}")


def log_exception(exception, context=""):
    """Log exception with full context and traceback"""
    error_msg = f"Exception occurred: {str(exception)}"
    if context:
        error_msg = f"Exception in {context}: {str(exception)}"

    logger.error(error_msg)
    logger.error(f"Exception type: {type(exception).__name__}")
    logger.error(f"Full traceback:\n{traceback.format_exc()}")


def log_function_error(func_name, exception, params=None):
    """Log function-specific errors with parameters"""
    logger.error(f"Function '{func_name}' failed: {str(exception)}")
    if params:
        logger.error(f"Function parameters: {params}")
    logger.error(f"Exception type: {type(exception).__name__}")
    logger.error(f"Traceback:\n{traceback.format_exc()}")


def critical(message):
    """Log critical message"""
    logger.critical(message)


def debug_json(data, label="JSON_DATA"):
    """Log data as formatted JSON with proper indentation"""
    try:
        if data is None:
            debug(f"{label}: None")
            return

        # Convert to JSON with 4-space indentation
        json_str = json.dumps(data, indent=4, ensure_ascii=False, default=str)
        debug(f"{label}:\n{json_str}")

        # Validate the JSON by parsing it back
        json.loads(json_str)
        debug(f"{label}_VALIDATION: Valid JSON structure")

        # Log summary info
        if isinstance(data, list):
            debug(f"{label}_SUMMARY: List with {len(data)} items")
        elif isinstance(data, dict):
            debug(f"{label}_SUMMARY: Dict with keys: {list(data.keys())}")
        else:
            debug(f"{label}_SUMMARY: Type {type(data).__name__}")

    except (TypeError, ValueError) as e:
        error(f"Failed to convert {label} to JSON: {str(e)}")
        debug(f"{label}_RAW: {str(data)}")
    except Exception as e:
        error(f"Unexpected error logging {label}: {str(e)}")
