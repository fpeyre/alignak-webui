#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
#   Frederic Mohier, frederic.mohier@alignak.net
#
# This file is part of (WebUI).
#
# (WebUI) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (WebUI) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.
"""
    Application logs
"""
from __future__ import print_function
import os
import sys

# Logs
import logging
from logging import Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler

from termcolor import cprint

# Default values for root logger
ROOT_LOGGER_NAME = 'alignak_webui'
ROOT_LOGGER_LEVEL = logging.INFO

# Default ISO8601 UTC date formatting:
HUMAN_DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'

# Default log formatter (no human timestamp)
DEFAULT_FORMATTER_NAMED = Formatter('[%(created)i] %(levelname)s: [%(name)s] %(message)s')

# Human timestamped log formatter
HUMAN_FORMATTER_NAMED = Formatter('[%(asctime)s] %(levelname)s: [%(name)s] %(message)s',
                                  HUMAN_DATE_FORMAT)

# Time rotation for file logger
ROTATION_WHEN = 'midnight'
ROTATION_INTERVAL = 1
ROTATION_COUNT = 5


logger = logging.getLogger(ROOT_LOGGER_NAME)  # pylint: disable=C0103
logger.setLevel(ROOT_LOGGER_LEVEL)


class ColorStreamHandler(StreamHandler):
    """
    This log handler provides colored logs when logs are emitted to a tty.
    """
    def emit(self, record):
        try:
            msg = self.format(record)
            colors = {'DEBUG': 'cyan', 'INFO': 'green', 'WARNING': 'yellow',
                      'CRITICAL': 'magenta', 'ERROR': 'red'}
            cprint(msg, colors[record.levelname])
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'ignore'))
        except TypeError:
            self.handleError(record)


# pylint: disable=too-many-arguments
def setup_logger(logger_, level=logging.INFO, log_file=None, log_console=True,
                 when=ROTATION_WHEN, interval=ROTATION_INTERVAL, backup_count=ROTATION_COUNT,
                 human_log=True, human_date_format=HUMAN_DATE_FORMAT):
    """
    Configure the provided logger
    - appends a ColorStreamHandler if it is not yet present
    - manages the formatter according to the required timestamp
    - appends a TimedRotatingFileHandler if it is not yet present for the same file
    - update level and formatter for already existing handlers

    :param logger_: logger object to configure. If None, configure the root logger
    :param level: log level
    :param log_file:
    :param log_console: True to configure the console stream handler
    :param human_log: use a human readeable date format
    :param when:
    :param interval:
    :param backup_count:
    :param human_date_format
    :return: the modified logger object
    """
    if logger_ is None:
        logger_ = logging.getLogger(ROOT_LOGGER_NAME)

    # Set logger level
    if level is not None:
        if not isinstance(level, int):
            level = getattr(logging, level, None)
        logger_.setLevel(level)

    formatter = DEFAULT_FORMATTER_NAMED
    if human_log:
        formatter = Formatter('[%(asctime)s] %(levelname)s: [%(name)s] %(message)s',
                              human_date_format)

    if log_console and hasattr(sys.stdout, 'isatty'):
        for handler in logger_.handlers:
            if isinstance(handler, ColorStreamHandler):
                if handler.level != level:
                    handler.setLevel(level)
                handler.setFormatter(formatter)
                break
        else:
            csh = ColorStreamHandler(sys.stdout)
            csh.setFormatter(formatter)
            logger_.addHandler(csh)

    if log_file:
        for handler in logger_.handlers:
            if isinstance(handler, TimedRotatingFileHandler) \
                    and handler.baseFilename == os.path.abspath(log_file):
                if handler.level != level:
                    handler.setLevel(level)
                handler.setFormatter(formatter)
                break
        else:
            file_handler = TimedRotatingFileHandler(log_file,
                                                    when=when, interval=interval,
                                                    backupCount=backup_count)
            file_handler.setFormatter(formatter)
            logger_.addHandler(file_handler)

    return logger_
