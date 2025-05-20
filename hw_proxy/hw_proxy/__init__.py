"""hw_proxy Package"""
import logging

from hw_proxy.__version__ import VERSION


class AppFilter(logging.Filter):
    """
    Class used to add a custom entry into the logger
    """

    def filter(self, record):
        record.app_version = f"hw_proxy-{VERSION}"
        return True


class CustomFormatter(logging.Formatter):
    """Logging custom formatter."""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self,
                 fmt: str,
                 date_format: str = "%Y-%m-%d %H:%M:%S"
                 ):
        super().__init__()
        self.fmt = fmt
        self.date_format = date_format
        self.colors_format = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.WARN: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.colors_format.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.date_format)
        return formatter.format(record)


def configure_logging(debug=None):
    """
    Prepare log folder in current home directory.

    :param debug: If true, set the lof level to debug

    """
    log = logging.getLogger("hw_proxy")
    log.addFilter(AppFilter())
    log.propagate = False
    syslog = logging.StreamHandler()
    syslog.setLevel(logging.DEBUG)

    formatter = CustomFormatter(
        '%(asctime)s :: %(app_version)s :: %(message)s', "%Y-%m-%d %H:%M:%S"
    )
    syslog.setFormatter(formatter)

    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    # add the handlers to logger
    log.addHandler(syslog)

    log.debug("Logger ready")