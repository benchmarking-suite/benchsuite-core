# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)
import configparser
import os
from abc import ABC, abstractmethod

import sys

import logging

from benchsuite.core.model.exception import ControllerConfigurationException

logger = logging.getLogger(__name__)


class StorageConnector(ABC):

    @abstractmethod
    def save_execution_result(self, execution_result):
        """
        saves an execution result on the storage backend
        :param execution_result: the execution result to save
        """
        pass

    @staticmethod
    @abstractmethod
    def load_from_config(config):
        pass

class SimpleFileBackend(StorageConnector):

    def load_from_config(config):
        logger.debug('Loading %s', SimpleFileBackend.__module__ + "." + __class__.__name__)


def load_storage_connector_from_config_string(config_string):
    config = configparser.ConfigParser()
    config.read_string(config_string)
    return load_storage_connector_from_config(config)

def load_storage_connector_from_config(config):
    storage_class = config['Storage']['class']

    module_name, class_name = storage_class.rsplit('.', 1)

    __import__(module_name)
    module = sys.modules[module_name]
    clazz = getattr(module, class_name)

    return clazz.load_from_config(config)

def load_storage_connector_from_config_file(config_file):
    if not os.path.isfile(config_file):
        raise ControllerConfigurationException('Config file {0} does not exist'.format(config_file))

    config = configparser.ConfigParser()
    config.read(config_file)
    return load_storage_connector_from_config(config)
