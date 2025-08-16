# log_config.py
"""Configure logging for the embedding service."""
import logging

# Configure logging (only console output)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
### embed_logger name for the logger
logger = logging.getLogger("embed_logger")
