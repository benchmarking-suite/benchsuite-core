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
import glob
import os
import ntpath

import logging
from appdirs import user_data_dir, user_config_dir

from benchsuite.core.model.exception import ControllerConfigurationException

CONFIG_FOLDER_VARIABLE_NAME = 'BENCHSUITE_CONFIG_FOLDER'
logger = logging.getLogger(__name__)


class ServiceProviderConfiguration():
    """
    Represents the configuration file of a cloud provider
    """

    def __init__(self, config_file):
        self.name = ntpath.basename(config_file)[:-5]

        config = configparser.ConfigParser()
        config.read(config_file)

        sections = [s for s in list(config.keys()) if s != 'DEFAULT' and s != 'provider']

        self.service_types = sections

    def __str__(self) -> str:
        return '{0}: {1}'.format(self.name, self.service_types)


class BenchmarkConfiguration():
    """
    Represents the configuration of a benchmark tol
    """

    def __init__(self, config_file):
        self.name = ntpath.basename(config_file)[:-5]

        config = configparser.ConfigParser()
        config.read(config_file)

        sections = [s for s in list(config.keys()) if s != 'DEFAULT']

        self.workloads = sections

    def __str__(self) -> str:
        return '{0}: {1}'.format(self.name, self.workloads)


class ControllerConfiguration():

    CLOUD_PROVIDERS_DIR = 'providers'
    BENCHMARKS_DIR = 'benchmarks'
    STORAGE_CONFIG_FILE = 'storage.conf'

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

    def get_providers(self):
        """
        Lists all the ServiceProvider configuration files found in the configuration folders
        :return: 
        """
        providers = []

        if self.alternative_config_dir:
            for n in glob.glob(os.path.join(self.alternative_config_dir, self.CLOUD_PROVIDERS_DIR, '*.conf')):
                providers.append(ServiceProviderConfiguration(n))

        for n in glob.glob(os.path.join(self.default_config_dir, self.CLOUD_PROVIDERS_DIR, '*.conf')):
            providers.append(ServiceProviderConfiguration(n))

        return providers

    def get_provider_by_name(self, name: str) -> ServiceProviderConfiguration:

        if self.alternative_config_dir:
            for n in glob.glob(os.path.join(self.alternative_config_dir, self.CLOUD_PROVIDERS_DIR, name + '.conf')):
                return ServiceProviderConfiguration(n)

        for n in glob.glob(os.path.join(self.default_config_dir, self.CLOUD_PROVIDERS_DIR, name + '.conf')):
            return ServiceProviderConfiguration(n)

        raise ControllerConfigurationException('Provider with name {0} does not exist'.format(name))


    def get_benchmarks(self):
        """
        Lists all the Benchmarks configuration files found in the configuration folders
        :return: 
        """
        benchmarks = []

        if self.alternative_config_dir:
            for n in glob.glob(os.path.join(self.alternative_config_dir, self.BENCHMARKS_DIR, '*.conf')):
                benchmarks.append(BenchmarkConfiguration(n))

        for n in glob.glob(os.path.join(self.default_config_dir, self.BENCHMARKS_DIR, '*.conf')):
            benchmarks.append(BenchmarkConfiguration(n))

        return benchmarks


    def get_benchmark_by_name(self, name):

        if self.alternative_config_dir:
            for n in glob.glob(os.path.join(self.alternative_config_dir, self.BENCHMARKS_DIR, name + '.conf')):
                return BenchmarkConfiguration(n)

        for n in glob.glob(os.path.join(self.default_config_dir, self.BENCHMARKS_DIR, name + '.conf')):
            return BenchmarkConfiguration(n)

        raise ControllerConfigurationException('Benchmark with name {0} does not exist'.format(name))


    # TODO: add an alternative location (based on environment variable)
    def get_storage_config_file(self):
        """
        Returns the configuration file for the storage.
        :return: 
        """
        if self.alternative_config_dir:
            file = os.path.join(self.alternative_config_dir, self.STORAGE_CONFIG_FILE)

            if os.path.isfile(file):
                return file

        file = os.path.join(self.default_config_dir, self.STORAGE_CONFIG_FILE)
        if os.path.isfile(file):
            return file

        raise ControllerConfigurationException('Storage configuration file not found')

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
