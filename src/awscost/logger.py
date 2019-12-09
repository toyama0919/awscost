import logging
from logging import getLogger, INFO, DEBUG


def get_logger(debug=False):
    log_fmt = "%(asctime)s %(levelname)s - %(message)s"
    logging.basicConfig(format=log_fmt)

    logger = getLogger(__name__)
    if debug:
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)
    return logger
