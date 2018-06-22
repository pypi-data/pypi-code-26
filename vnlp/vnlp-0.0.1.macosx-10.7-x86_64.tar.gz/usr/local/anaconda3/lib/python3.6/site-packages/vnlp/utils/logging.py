import logging


def get_logger(name, fout=None, level=logging.INFO, file_level=None):
    """
    Returns a `logging.Logger` object that outputs to stdout and optionally to disk.
    """
    logger = logging.Logger(name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if fout:
        fh = logging.FileHandler(fout)
        fh.setLevel(file_level or level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
