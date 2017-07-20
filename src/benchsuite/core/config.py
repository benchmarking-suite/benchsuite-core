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




import os

import logging
from appdirs import user_data_dir, user_config_dir

from benchsuite.core.model.exception import ControllerConfigurationException

CONFIG_FOLDER_VARIABLE_NAME = 'BENCHSUITE_CONFIG_FOLDER'
logger = logging.getLogger(__name__)


class ControllerConfiguration():

    CLOUD_PROVIDERS_DIR = 'providers'
    BENCHMARKS_DIR = 'benchmarks'

    def __init__(self, alternative_config_dir=None):
        self.default_config_dir = os.path.join(user_config_dir(), 'benchmarking-suite')

        self.alternative_config_dir = alternative_config_dir

        if CONFIG_FOLDER_VARIABLE_NAME in os.environ and not self.alternative_config_dir:
            self.alternative_config_dir = os.environ[CONFIG_FOLDER_VARIABLE_NAME]

        logger.debug('Using default configuration directory: %s', self.default_config_dir)
        logger.debug('Using alternative configuration directory: %s', self.alternative_config_dir)

    def get_default_data_dir(self):
        d = user_data_dir('benchmarking-suite', None)
        if not os.path.exists(d):
            os.makedirs(d)
        return d

    def get_provider_config_file(self, name):

        if os.path.isfile(name):
            return name

        if self.alternative_config_dir:
            file = os.path.join(self.alternative_config_dir, self.CLOUD_PROVIDERS_DIR, name + ".conf")

            if os.path.isfile(file):
                return file

        file = os.path.join(self.default_config_dir, self.CLOUD_PROVIDERS_DIR, name + ".conf")

        if os.path.isfile(file):
            return file

        raise ControllerConfigurationException('Impossible to find prodiver configuration for {0}'.format(name))

    def get_benchmark_config_file(self, name):

        if os.path.isfile(name):
            return name

        if self.alternative_config_dir:
            file = os.path.join(self.alternative_config_dir, self.BENCHMARKS_DIR, name + ".conf")

            if os.path.isfile(file):
                return file

        file = os.path.join(self.default_config_dir, self.BENCHMARKS_DIR, name + ".conf")

        if os.path.isfile(file):
            return file

        raise ControllerConfigurationException('Impossible to find benchmark configuration for {0}'.format(name))
