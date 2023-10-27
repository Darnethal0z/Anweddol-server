"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module defines the 'anwdlserver' CLI executable server process.

"""

from zipfile import ZipFile
import datetime
import logging

# Constants definition
LOG_INFO = "INFO"
LOG_WARN = "WARNING"
LOG_ERROR = "ERROR"


class AnweddolServerCLILoggingManager:
    def __init__(self, log_file_path, enable_stdout_log=False):
        self.log_file_path = log_file_path
        self.enable_stdout_log = enable_stdout_log

        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(message)s",
            filename=self.log_file_path,
            level=logging.INFO,
            encoding="utf-8",
            filemode="a",
        )

    def log(self, kind, message):
        if kind == LOG_INFO:
            logging.info(message)

        elif kind == LOG_WARN:
            logging.warning(message)

        else:
            logging.error(message)

        if self.enable_stdout_log:
            print(f"{datetime.datetime.now()} {kind} : {message}")

    def rotate(self, archive=True, log_archive_folder_path=None):
        if archive:
            ZipFile(
                log_archive_folder_path
                + ("/" if log_archive_folder_path[-1] != "/" else "")
                + f"archived_{datetime.datetime.now()}.zip",
                "w",
            ).write(self.log_file_path)

        # Open the log file path in write mode to erase its content
        with open(self.log_file_path, "w") as fd:
            fd.close()
