import sys
from loguru import logger

logger.remove()
logger.add(
    "prism_{time:YYYY-MM-DD_HH-mm-ss}.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level="DEBUG"
)

def handle_exception(exc: Exception, user_message: str = "An error occurred", critical: bool = False):
    """
    Handles exceptions by logging the error and optionally exiting the program if the error is critical.

    :param exc: The exception instance to handle.
    :param user_message: A message to display to the end user.
    :param critical: If True, the program will exit after handling the exception.
    """
    log_function = logger.error if not critical else logger.critical
    log_function(f"{user_message}: {exc}")
    print(f"[-] {user_message}")
    if critical:
        sys.exit(1)