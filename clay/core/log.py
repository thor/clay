"""
Logger implementation.
"""
from threading import Lock
from datetime import datetime
from enum import IntEnum


from . import EventHook, settings


class LogLevel(IntEnum):
    debug = 0
    info = 1
    warning = 2
    error = 3


class _LoggerRecord(object):
    """
    Represents a logger record.
    """
    def __init__(self, verbosity, message, args):
        self._timestamp = datetime.now()
        self._verbosity = verbosity
        self._message = message
        self._args = args

    @property
    def formatted_timestamp(self):
        """
        Return timestamp.
        """
        return str(self._timestamp)

    @property
    def verbosity(self):
        """
        Return verbosity.
        """
        return self._verbosity

    @property
    def formatted_message(self):
        """
        Return formatted message.
        """
        return self._message % self._args


class _Logger(object):
    """
    Global logger.

    Allows subscribing to log events.
    """

    def __init__(self):
        self.logs = []
        self.logfile = open('/tmp/clay.log', 'w')

        self._lock = Lock()
        self.on_log_event = EventHook()

        verbosity = settings.settings_manager.get('debug_level', 'clay_settings')

        for level in LogLevel:
            if level.name == verbosity:
                self._verbosity = level
                return
        else:
            self._verbosity = LogLevel.error
            self.error("Unknown loglevel: '%s'" % verbosity)

    def log(self, level, message, *args):
        """
        Add log item.
        """
        self._lock.acquire()
        try:
            if level < self._verbosity:
                return

            logger_record = _LoggerRecord(level, message, args)
            self.logs.append(logger_record)
            self.logfile.write('{} {:8} {}\n'.format(
                logger_record.formatted_timestamp,
                logger_record.verbosity,
                logger_record.formatted_message
            ))
            self.logfile.flush()
            self.on_log_event.fire(logger_record)
        finally:
            self._lock.release()

    def debug(self, message, *args):
        """
        Add debug log item.
        """
        self.log(LogLevel.debug, message, *args)

    def info(self, message, *args):
        """
        Add info log item.
        """
        self.log(LogLevel.info, message, *args)

    def warn(self, message, *args):
        """
        Add warning log item.
        """
        self.log(LogLevel.warn, message, *args)

    warning = warn

    def error(self, message, *args):
        """
        Add error log item.
        """
        self.log(LogLevel.error, message, *args)

    def get_logs(self):
        """
        Return all logs.
        """
        return self.logs


logger = _Logger()
