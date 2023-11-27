"""
Copyright 2023 NovAtel Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module Description: Holds classes and functions for logging.
"""
from ctypes import *

from novatel_edie.common import LogLevelEnum
from novatel_edie.decoders.common import DECODERS_DLL

DECODERS_DLL.common_logger_setup.restype = None
DECODERS_DLL.common_logger_setup.argtypes = None
DECODERS_DLL.common_logger_setup_from_file.restype = None
DECODERS_DLL.common_logger_setup_from_file.argtypes = [c_char_p]
DECODERS_DLL.common_logger_set_logger_level.restype = c_bool
DECODERS_DLL.common_logger_set_logger_level.argtypes = [c_int32]
DECODERS_DLL.common_logger_shutdown_logger.restype = None
DECODERS_DLL.common_logger_shutdown_logger.argtypes = None
DECODERS_DLL.common_logger_log.restype = c_bool
DECODERS_DLL.common_logger_log.argtypes = [c_int32, c_char_p]


class Logger:
    """Logger class capable of debug logging.
    """

    def __init__(self, logger_configfile: str = None):
        """Initializer.

        Args:
            logger_configfile: logging config file.
        """
        if logger_configfile:
            DECODERS_DLL.common_logger_setup_from_file(str(logger_configfile).encode())
        else:
            DECODERS_DLL.common_logger_setup()

    @staticmethod
    def set_logger_level(logger_level: LogLevelEnum):
        """Sets the logging verbosity.

        Args:
            logger_level: logging config verbosity enum.
        """
        DECODERS_DLL.common_logger_set_logger_level(logger_level.value)

    @staticmethod
    def shutdown_logger():
        """Shuts down the logger.
        """
        DECODERS_DLL.common_logger_shutdown_logger()

    @staticmethod
    def trace(message: str):
        """Adds a trace message to the logger output.

        Args:
            message: Trace string to add to the logging output.
        """
        DECODERS_DLL.common_logger_log(LogLevelEnum.TRACE.value, str(message).encode())

    @staticmethod
    def debug(message: str):
        """Adds a debug message to the logger output.

        Args:
            message: Debug string to add to the logging output.
        """
        DECODERS_DLL.common_logger_log(LogLevelEnum.DEBUG.value, str(message).encode())

    @staticmethod
    def info(message: str):
        """Adds an info message to the logger output.

        Args:
            message: Info string to add to the logging output.
        """
        DECODERS_DLL.common_logger_log(LogLevelEnum.INFO.value, str(message).encode())

    @staticmethod
    def warn(message: str):
        """Adds a warning message to the logger output.

        Args:
            message: Warning string to add to the logging output.
        """
        DECODERS_DLL.common_logger_log(LogLevelEnum.WARN.value, str(message).encode())

    @staticmethod
    def error(message: str):
        """Adds an error message to the logger output.

        Args:
            message: Error string to add to the logging output.
        """
        DECODERS_DLL.common_logger_log(LogLevelEnum.ERR.value, str(message).encode())

    @staticmethod
    def critical(message: str):
        """Adds a critical message to the logger output.

        Args:
            message: Critical string to add to the logging output.
        """
        DECODERS_DLL.common_logger_log(LogLevelEnum.CRITICAL.value, str(message).encode())
