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
import json
import os
import re

import logging
from appdirs import user_data_dir, user_config_dir

from benchsuite.core.model.exception import ControllerConfigurationException

logger = logging.getLogger(__name__)


class ServiceProviderConfiguration():
    """
    Represents the configuration file of a cloud provider
    """

    def __init__(self, config_file):
        self.name = os.path.splitext(os.path.basename(config_file))[0]

        # TODO: use here the functions in provider.py to load the providers from the configuration
        try:
            with open(config_file) as f:
                config = configparser.ConfigParser()
                config.read_dict(json.load(f))
        except ValueError as ex:
            logger.warning('Got an exception trying to decode configuration file as json: ' + str(ex))
            try:
                config = configparser.ConfigParser()
                config.read(config_file)
            except Exception as ex:
                raise ControllerConfigurationException('Invalid configuration provided: {0}'.format(str(ex)))

        # TODO: libcloud_extra_params should not go here because it is something dependant from the implemetnation of
        sections = [s for s in list(config.keys()) if s != 'DEFAULT' and s != 'provider' and s != 'libcloud_extra_params']

        self.service_types = sections

    def __str__(self) -> str:
        return '{0}: {1}'.format(self.name, self.service_types)


class BenchmarkToolConfiguration():
    """
    Represents the configuration of a benchmark tool
    """

    def __init__(self, config_file):
        self.id = os.path.basename(config_file)[:-5]

        config = configparser.ConfigParser()
        config.read(config_file)

        self.tool_name = config['DEFAULT']['tool_name']

        sections = [s for s in list(config.keys()) if s != 'DEFAULT']

        self.workloads = []

        for w in sections:
            self.workloads.append({
                'id': w,
                'workload_name': config[w]['workload_name'] if 'workload_name' in config[w] else None,
                'workload_description': config[w]['workload_description'] if 'workload_description' in config[w] else None
            })

    def find_workloads(self, regex):
        return [w['id'] for w in self.workloads if re.match(regex, w['id'])]

    def __str__(self) -> str:
        return '{0}: {1}'.format(self.name, self.workloads)


class ControllerConfiguration():
    '''
    Model the Benchmarking Suite configuration.
    '''

    CLOUD_PROVIDERS_DIR = 'providers'
    BENCHMARKS_DIR = 'benchmarks'
    STORAGE_CONFIG_FILE = 'storage.conf'
    STORAGE_JSON_CONFIG_FILE = 'storage.json'

    def __init__(self, alternative_config_dir=None):

        self.default_config_dir = os.path.join(user_config_dir(), 'benchmarking-suite')

        self.alternative_config_dir = alternative_config_dir

        logger.debug('Using default configuration directory: %s', self.default_config_dir)
        logger.debug('Using alternative configuration directory: %s', self.alternative_config_dir)

    def get_default_data_dir(self):
        d = user_data_dir('benchmarking-suite', None)
        if not os.path.exists(d):
            os.makedirs(d)
        return d

    def list_available_providers(self):
        """
        Lists all the ServiceProvider configuration files found in the configuration folders
        :return: 
        """
        providers = []

        if self.alternative_config_dir:
            for f in os.listdir(os.path.join(self.alternative_config_dir, self.CLOUD_PROVIDERS_DIR)):
                if os.path.splitext(f)[1] in ['.conf', '.json']:
                    try:
                        n = os.path.join(self.alternative_config_dir, self.CLOUD_PROVIDERS_DIR, f)
                        providers.append(ServiceProviderConfiguration(n))
                    except ControllerConfigurationException:
                        pass


        for f in os.listdir(os.path.join(self.default_config_dir, self.CLOUD_PROVIDERS_DIR)):
            if os.path.splitext(f)[1] in ['.conf', '.json']:
                try:
                    n = os.path.join(self.default_config_dir, self.CLOUD_PROVIDERS_DIR, f)
                    providers.append(ServiceProviderConfiguration(n))
                except ControllerConfigurationException:
                    pass

        return providers

    def list_available_tools(self):
        """
        Lists all the Benchmarks configuration files found in the configuration folders
        :return: 
        """
        benchmarks = []

        if self.alternative_config_dir:
            for n in glob.glob(os.path.join(self.alternative_config_dir, self.BENCHMARKS_DIR, '*.conf')):
                benchmarks.append(BenchmarkToolConfiguration(n))

        for n in glob.glob(os.path.join(self.default_config_dir, self.BENCHMARKS_DIR, '*.conf')):
            benchmarks.append(BenchmarkToolConfiguration(n))

        return benchmarks

    def get_provider_by_name(self, name: str) -> ServiceProviderConfiguration:
        return ServiceProviderConfiguration(self.get_provider_config_file(name))

    def get_benchmark_by_name(self, name):

        if self.alternative_config_dir:
            for n in glob.glob(os.path.join(self.alternative_config_dir, self.BENCHMARKS_DIR, name + '.conf')):
                return BenchmarkToolConfiguration(n)

        for n in glob.glob(os.path.join(self.default_config_dir, self.BENCHMARKS_DIR, name + '.conf')):
            return BenchmarkToolConfiguration(n)

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

            file = os.path.join(self.alternative_config_dir, self.STORAGE_JSON_CONFIG_FILE)
            if os.path.isfile(file):
                return file

        file = os.path.join(self.default_config_dir, self.STORAGE_CONFIG_FILE)
        if os.path.isfile(file):
            return file

        file = os.path.join(self.default_config_dir, self.STORAGE_JSON_CONFIG_FILE)
        if os.path.isfile(file):
            return file

        raise ControllerConfigurationException('Storage configuration file not found')

    def get_provider_config_file(self, name):

        if os.path.isfile(name):
            return name

        if self.alternative_config_dir:
            for f in os.listdir(os.path.join(self.alternative_config_dir, self.CLOUD_PROVIDERS_DIR)):
                if os.path.splitext(f)[0] == name:
                    return os.path.join(self.alternative_config_dir, self.CLOUD_PROVIDERS_DIR, f)


        for f in os.listdir(os.path.join(self.default_config_dir, self.CLOUD_PROVIDERS_DIR)):
            if os.path.splitext(f)[0] == name:
                return os.path.join(self.default_config_dir, self.CLOUD_PROVIDERS_DIR, f)

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
