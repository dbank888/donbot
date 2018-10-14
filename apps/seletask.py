import logging
from copy import deepcopy
from pathlib import Path

from logzero import setup_logger

import sys
# sys.path.append(sys.path[0] + "/..")

from seleplus.seleplus import LOG_DIR, FirefoxPlus, new_windows_opened


class SeleTask(object):

    name = 'SeleTask'

    def __init__(self, config):
        self._config = deepcopy(config)
        self.task = config['task']
        self.extra = config.get('extra', {})
        self.task_name = self.get_task_name()

        self.logger = self.get_logger()
        self.file_logger = self.get_file_logger()

        self.s_config = {}
        self.s_config['task_name'] = self.task_name
        self.s_config['driver'] = config.get('driver', {})
        self.s_config['prefs'] = config.get('prefs', {})
        self.s = FirefoxPlus(self.s_config)

    def get_task_name(self):
        task_name = self.task
        return task_name

    def get_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = setup_logger(self.task_name, formatter=formatter)
        logger.setLevel(logging.DEBUG)

        return logger

    def get_file_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        file_logger = setup_logger(
            self.task_name + '_file',
            logfile=str(Path(LOG_DIR, self.task_name + '.log')),
            level=logging.INFO,
            formatter=formatter,
            fileLoglevel=logging.INFO
        )

        return file_logger
