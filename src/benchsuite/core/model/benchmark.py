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
import sys
from abc import abstractmethod

from benchsuite.core.model.exception import ControllerConfigurationException


class Benchmark:
    """
    A Benchmark
    """

    def __init__(self, tool_id, workload_id, tool_name, workload_name,
                 workload_categories,
                 workload_description):
        self.tool_id = tool_id
        self.workload_id = workload_id
        self.tool_name = tool_name
        self.workload_name = workload_name
        self.workload_categories = workload_categories
        self.workload_description = workload_description

    @staticmethod
    @abstractmethod
    def load_from_config_file(config, tool, workload):
        pass

    @abstractmethod
    def get_env_request(self):
        pass

    @abstractmethod
    def prepare(self, execution):
        pass

    @abstractmethod
    def execute(self, execution, async=False):
        pass

    @abstractmethod
    def get_result(self, execution):
        pass

    @abstractmethod
    def get_runtime(self, execution, phase):
        pass



def load_benchmark_from_config_file(config_file, tool, workload):
    if not os.path.isfile(config_file):
        raise ControllerConfigurationException('Config file {0} does not exist'.format(config_file))

    config = configparser.ConfigParser()
    config.read(config_file)


    provider_class = config['DEFAULT']['class']

    module_name, class_name = provider_class.rsplit('.', 1)

    __import__(module_name)
    module = sys.modules[module_name]
    clazz = getattr(module, class_name)

    return clazz.load_from_config_file(config, tool, workload)