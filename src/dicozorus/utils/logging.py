from logging import (getLogger, DEBUG, INFO, WARNING, ERROR, CRITICAL,
        Formatter as _Formatter, StreamHandler)
from dicozorus.utils.colors import Colors

# Default logger
LOGGER = getLogger('dicozorus')

class Formatter(_Formatter):
    """
    Dicozorus Logging Formatter.

    Replaces default level names with symbols.
    Color support.
    """

    levelnames = {
        DEBUG: '[*]',
        INFO: '[+]',
        WARNING: '[!]',
        ERROR: '[x]',
        CRITICAL: '[x]',
    }

    colored_levelnames = {
        DEBUG: Colors.blue('[*]'),
        INFO: Colors.green('[+]'),
        WARNING: Colors.yellow('[!]'),
        ERROR: Colors.red('[x]'),
        CRITICAL: Colors.red('[x]'),
    }

    def __init__(self, *args, colors=True, **kwargs):
        """
        Initialization.

        :param args: wrapped
        :param colors: enable color support
        :param kwargs: wrapped
        """

        super().__init__(*args, **kwargs)
        self.colors = colors
        if self.colors:
            self.levelnames = self.colored_levelnames

    def format(self, record):
        """
        Custom format function.

        Replaces record's levelname with the corresponding one in self.levelnames.
        Revert changes after formatting.
        """

        bak = record.levelname
        record.levelname = self.levelnames[record.levelno]
        formated_record = super().format(record)
        record.levelname = bak
        return formated_record


def configure(logger=None, debug=False, colors=True, datefmt='%y/%m/%d %H:%M:%S'):
    """
    Logger configuration.
    """
    logger = logger or LOGGER

    handler = StreamHandler()
    formatter = Formatter('%(levelname)s %(message)s', datefmt=datefmt, colors=colors)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Logs level
    level = DEBUG if debug else INFO
    logger.setLevel(level)

    return logger
