import logging

try:
    import coloredlogs
    colored = True
except:
    colored = False


def get_logger(name='cinemabits'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    fmt = '%(msg)s'

    if colored:
        coloredlogs.install(fmt=fmt)
    else:
        fmt = logging.Formatter(fmt)
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    return logger
