import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)

logger = logging.getLogger("ContentAI")