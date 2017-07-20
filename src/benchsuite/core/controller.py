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


import logging
import os
from typing import Dict

from benchsuite.core.config import ControllerConfiguration
from benchsuite.core.model.benchmark import load_benchmark_from_config_file
from benchsuite.core.model.exception import ControllerConfigurationException, UndefinedExecutionException
from benchsuite.core.model.execution import BenchmarkExecution
from benchsuite.core.model.provider import load_service_provider_from_config_file, load_provider_from_config_string
from benchsuite.core.model.session import BenchmarkingSession
from benchsuite.core.session import SessionStorageManager

STORAGE_FOLDER_VARIABLE_NAME = 'BENCHSUITE_STORAGE_FOLDER'


logger = logging.getLogger(__name__)



class BenchmarkingController():
    """
    The main class to control the benchmarking
    """

    def __init__(self, config_folder=None, storage_dir=None):

        self.config_folder = config_folder
        if self.config_folder:
            logger.info('Using custom config directory at ' + self.config_folder)
        self.configuration = ControllerConfiguration(self.config_folder)

        self.storage_folder = storage_dir or self.configuration.get_default_data_dir()
        self.session_storage = SessionStorageManager(self.storage_folder)
        self.session_storage.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session_storage.store()
        return exc_type is None

    def list_sessions(self) -> Dict[str, BenchmarkingSession]:
        """
        Lists the sessions
        :return: Session list
        """
        return self.session_storage.list()

    def list_executions(self):
        return [item for sublist in self.list_sessions() for item in sublist.list_executions()]

    def get_session(self, session_id: str) -> BenchmarkingSession:
        return self.session_storage.get(session_id)

    def new_session(self, cloud_provider_name: str, cloud_service_name: str) -> BenchmarkingSession:
        c = self.configuration.get_provider_config_file(cloud_provider_name)
        p = load_service_provider_from_config_file(c, cloud_service_name)
        s = BenchmarkingSession(p)
        self.session_storage.add(s)
        return s

    def new_session_by_config_string(self, configuration_string: str) -> BenchmarkingSession:
        p = load_provider_from_config_string(configuration_string)
        s = BenchmarkingSession(p)
        self.session_storage.add(s)
        return s


    def destroy_session(self, session_id: str) -> None:
        s = self.get_session(session_id)
        logger.debug('Session loaded: {0}'.format(s))
        s.destroy()
        self.session_storage.remove(s)

    def get_execution(self, exec_id, session_id=None):
        if session_id:
            return self.session_storage.get(session_id).get_execution(exec_id)

        for s in self.session_storage.list():
            try:
                return s.get_execution(exec_id)
            except:
                pass

        raise UndefinedExecutionException('Execution with id={0} does not exist'.format(exec_id))

    def new_execution(self, session_id: str, tool: str, workload: str) -> BenchmarkExecution:
        s = self.session_storage.get(session_id)
        config_file = self.configuration.get_benchmark_config_file(tool)
        b = load_benchmark_from_config_file(config_file, workload)
        e = s.new_execution(b)
        return e

    def prepare_execution(self, exec_id, session_id=None):
        e = self.get_execution(exec_id, session_id)
        logger.debug("Execution loaded: {0}".format(e))
        return e.prepare()

    def run_execution(self, exec_id, async=False, session_id=None):
        e = self.get_execution(exec_id, session_id)
        return e.execute(async=async)


    def collect_execution_results(self, exec_id, session_id=None):
        e = self.get_execution(exec_id, session_id)
        return e.collect_result()


    def execute_onestep(self, provider, service_type: str, tool: str, workload: str) -> str:
        session = self.new_session(provider, service_type)
        execution = self.new_execution(session.id, tool, workload)
        execution.prepare()
        execution.execute()
        out, err = execution.collect_result()
        session.destroy()
        return out, err