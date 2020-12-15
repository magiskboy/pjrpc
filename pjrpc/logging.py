import logging


loglevel_name_map = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}


class PJRPCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        if datefmt is None:
            datefmt = '%Y-%m-%d %H:%M:%S'

        return super().formatTime(record, datefmt)


logger = logging.getLogger('pjrpc.server')
consoleHandler = logging.StreamHandler()
fmt = PJRPCFormatter('[%(asctime)-15s] %(message)s')
consoleHandler.setFormatter(fmt)
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)


def set_level(level_name):
    level = loglevel_name_map.get(level_name, 'error')
    logger.setLevel(level)
