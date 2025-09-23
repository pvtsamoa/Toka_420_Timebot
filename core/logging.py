import logging, sys
def setup_logging():
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout)
    return logging.getLogger("toka")
