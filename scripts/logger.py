import logging
import sys


def obter_logger(modulo):
    if not logging.root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%H:%M:%S",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
    return logging.getLogger(modulo)
