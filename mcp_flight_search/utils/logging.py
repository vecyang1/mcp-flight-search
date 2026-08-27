"""
Logging configuration for MCP Flight Search.
"""
import logging

try:
    from rich.logging import RichHandler
    _HANDLER = RichHandler(rich_tracebacks=True)
except ImportError:
    _HANDLER = logging.StreamHandler()

def setup_logging():
    """Configure and set up logging for the application."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="| %(levelname)-8s | %(name)s | %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[_HANDLER],
        force=True  # This is the fix that overrides uvicorn & third-party loggers
    )

    logger = logging.getLogger("flight_search")
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logger

# Create the logger instance for import by other modules
logger = setup_logging() 