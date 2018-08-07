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
import re
import logging
import traceback
from typing import Dict, Tuple, List

import datetime

from benchsuite.core.config import ControllerConfiguration
from benchsuite.core.model.benchmark import load_benchmark_from_config_file
from benchsuite.core.model.exception import ControllerConfigurationException, UndefinedExecutionException, \
    BashCommandExecutionFailedException, dump_BashCommandExecution_exception, NoExecuteCommandsFound
from benchsuite.core.model.execution import BenchmarkExecution, ExecutionError
from benchsuite.core.model.provider import load_service_provider_from_config_file, load_provider_from_config, \
    load_provider_from_config_string
from benchsuite.core.model.session import BenchmarkingSession
from benchsuite.core.model.storage import load_storage_connector_from_config_file, load_storage_connector_from_config_string
from benchsuite.core.sessionmanager import SessionStorageManager


CONFIG_FOLDER_ENV_VAR_NAME = 'BENCHSUITE_CONFIG_FOLDER'
DATA_FOLDER_ENV_VAR_NAME = 'BENCHSUITE_DATA_FOLDER'
PROVIDER_STRING_ENV_VAR_NAME = 'BENCHSUITE_PROVIDER'
SERVICE_TYPE_STRING_ENV_VAR_NAME = 'BENCHSUITE_SERVICE_TYPE'
STORAGE_CONFIG_FILE_ENV_VAR = 'BENCHSUITE_STORAGE_CONFIG'


logger = logging.getLogger(__name__)


class BenchmarkingController:
    """The facade to all Benchmarking Suite operations"""

    def __init__(self, config_folder=None, storage_config_file=None):

        if not config_folder and CONFIG_FOLDER_ENV_VAR_NAME in os.environ :
            config_folder = os.environ[CONFIG_FOLDER_ENV_VAR_NAME]

        self.configuration = ControllerConfiguration(config_folder)

        data_folder = self.configuration.get_default_data_dir()
        if DATA_FOLDER_ENV_VAR_NAME in os.environ:
            data_folder = os.environ[DATA_FOLDER_ENV_VAR_NAME]

        self.session_storage = SessionStorageManager(data_folder)
        self.session_storage.load()

        try:
            # different ways to load the storage configuration:
            # 1. use the storage_config_file argument if initialized (the -r option in the CLI)
            # 2. use the content of the BENCHSUITE_STORAGE_CONFIG environment variable
            # 3. use the default location in the configuration folder

            if storage_config_file:
                logger.info('Loading storage configuration from file ' + storage_config_file)
                self.results_storage = load_storage_connector_from_config_file(storage_config_file)
            elif STORAGE_CONFIG_FILE_ENV_VAR in os.environ:
                logger.info('Loading storage configuration from {0} env variable'.format(STORAGE_CONFIG_FILE_ENV_VAR))
                self.results_storage = load_storage_connector_from_config_string(os.environ[STORAGE_CONFIG_FILE_ENV_VAR])
            else:
                logger.info('Loading storage configuration from default location ' + self.configuration.get_storage_config_file())
                self.results_storage = load_storage_connector_from_config_file(self.configuration.get_storage_config_file())

        except ControllerConfigurationException:
            logger.warning('Results storage configuration file not found. Results storage of results is disabled')
            self.results_storage = None


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session_storage.store()
        return exc_type is None

    def list_available_providers(self):
        return self.configuration.list_available_providers()

    def list_available_benchmark_cfgs(self):
        return self.configuration.list_available_tools()

    def get_benchmark_cfg(self, name):
        return self.configuration.get_benchmark_by_name(name)

    #
    # SESSIONS
    #

    def list_sessions(self) -> Dict[str, BenchmarkingSession]:
        return self.session_storage.list()


    def get_session(self, session_id: str) -> BenchmarkingSession:
        return self.session_storage.get(session_id)

    def new_session(self, cloud_provider_name: str, cloud_service_name: str, properties={}) -> BenchmarkingSession:

        # service type is not provided via argument. Try to load from env variable
        # Even if not provided, it is fine if the provider has only one service type
        if not cloud_service_name and SERVICE_TYPE_STRING_ENV_VAR_NAME in os.environ:
            cloud_service_name = os.environ[SERVICE_TYPE_STRING_ENV_VAR_NAME]

        if not cloud_provider_name:
            # provider configuration is not provided via argument. Try to load from environment
            if PROVIDER_STRING_ENV_VAR_NAME in os.environ:
                provider_config = os.environ[PROVIDER_STRING_ENV_VAR_NAME]
                p = load_provider_from_config_string(provider_config, cloud_service_name)

            else:
                raise ControllerConfigurationException('Provider must be specified either '
                                                       'via argument (--provider) or via environment '
                                                       'variable ({0})'.format(PROVIDER_STRING_ENV_VAR_NAME))
        else:
            c = self.configuration.get_provider_config_file(cloud_provider_name)
            p = load_service_provider_from_config_file(c, cloud_service_name)

        s = BenchmarkingSession(p)
        s.add_all_props(properties)
        self.session_storage.add(s)
        return s

    def new_session_by_config(self, configuration_string: str) -> BenchmarkingSession:
        p = load_provider_from_config(configuration_string)
        s = BenchmarkingSession(p)
        self.session_storage.add(s)
        return s

    def destroy_session(self, session_id: str) -> None:
        s = self.get_session(session_id)
        logger.debug('Session loaded: {0}'.format(s))
        s.destroy()
        self.session_storage.remove(s)

    #
    # EXECUTIONS
    #

    def list_executions(self):
        return [item for sublist in self.list_sessions() for item in sublist.list_executions()]


    def get_execution(self, exec_id: str, session_id: str = None) -> BenchmarkExecution:
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
        logger.debug('Loading benchmark from configuration file %s', config_file)
        b = load_benchmark_from_config_file(config_file, tool, workload)
        e = s.new_execution(b)
        return e


    def __store_execution_error(self, execution: BenchmarkExecution, exception, phase):

        if not self.results_storage:
            logger.warning('Results storage not configured. The logging of the exception is disabled')
            return

        exec_err_obj = ExecutionError()
        exec_err_obj.timestamp = datetime.datetime.now()
        exec_err_obj.tool = execution.test.tool_id
        exec_err_obj.workload = execution.test.workload_id
        exec_err_obj.provider = execution.session.provider.get_provder_properties_dict()
        exec_err_obj.exec_env = execution.exec_env.get_specs_dict()
        exec_err_obj.phase = phase
        exec_err_obj.exception_type = type(exception).__name__
        exec_err_obj.exception_data = exception.__dict__
        exec_err_obj.traceback = traceback.format_exc()
        self.results_storage.save_execution_error(exec_err_obj)

    def prepare_execution(self, exec_id, session_id=None):
        e = self.get_execution(exec_id, session_id)
        logger.debug("Execution loaded: {0}".format(e))

        try:
            return e.prepare()

        except BashCommandExecutionFailedException as ex:
            error_file = 'last_cmd_error_{0}.dump'.format(exec_id)
            logger.error('Exception executing commands, dumping to {0}'.format(error_file))
            dump_BashCommandExecution_exception(ex, error_file)
            self.__store_execution_error(e, ex, 'prepare')
            logger.info('Continuing with the next test')
            raise ex

    def run_execution(self, exec_id, async=False, session_id=None):
        e = self.get_execution(exec_id, session_id)

        try:
            r = e.execute(async=async)

            if not async:
                self.store_execution_result(exec_id)

            return r

        except NoExecuteCommandsFound as ex:
            logger.error('The benchmark configuration does not define any command for this platform. Aborting the execution')
            self.__store_execution_error(e, ex, 'run')
            raise ex

        except BashCommandExecutionFailedException as ex:
            error_file = 'last_cmd_error_{0}.dump'.format(exec_id)
            logger.error('Exception executing commands, dumping to {0}'.format(error_file))
            dump_BashCommandExecution_exception(ex, error_file)
            self.__store_execution_error(e, ex, 'run')
            logger.info('Continuing with the next test')
            raise ex

    def collect_execution_results(self, exec_id, session_id=None):
        e = self.get_execution(exec_id, session_id)
        return e.collect_result()

    def store_execution_result(self, exec_id, session_id=None):
        e = self.get_execution(exec_id, session_id)
        if self.results_storage:
            r = e.get_execution_result()
            self.results_storage.save_execution_result(r)
        else:
            logger.warning('Result Storage not configured. Storage of results is disabled.')


    #
    # MULTIEXEC
    #
    def execute_onestep(self, provider, service_type: str,
                        tests: List[Tuple[str, str]],
                        new_session_props=None,
                        fail_on_error=False) -> None:

        if not service_type:
            s_types = self.configuration.get_provider_by_name(provider).service_types
        else:
            s_types = [service_type]

        for st in s_types:
            session = self.new_session(provider, st, properties=new_session_props)
            try:

                for tool, workload in tests:

                    if not workload:
                        workloads = [ w['id'] for w in self.configuration.get_benchmark_by_name(tool).workloads]
                    else:
                        if re.search(r'\*|\?', workload):
                            workloads = self.configuration.get_benchmark_by_name(tool).find_workloads(workload)
                        else:
                            workloads = [workload]

                    for w in workloads:
                        execution = self.new_execution(session.id, tool, w)
                        try:
                            self.prepare_execution(execution.id)
                            self.run_execution(execution.id)

                        except Exception as ex:
                            if fail_on_error:
                                logger.error('Unhandled exception({0}) running {1}:{2}. '
                                             'Stopping here because "--failonerror" option is set'.format(str(ex), tool, w))
                                raise ex
                            else:
                                logger.error('Unhandled exception ({0}) running {1}:{2}. '
                                             'Ignoring and continuing with the next test'.format(str(ex), tool, w))

            except Exception as ex:
                raise ex

            finally:  # make sure to always destroy the VMs created
                session.destroy()
                self.session_storage.remove(session)
