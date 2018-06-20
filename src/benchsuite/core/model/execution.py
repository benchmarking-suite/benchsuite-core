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

import time
import uuid
from abc import ABC, abstractmethod

import logging


logger = logging.getLogger(__name__)


class ExecutionResultParser(ABC):

    @abstractmethod
    def get_metrics(self, stdout, stderr):
        """
        Parsers the execution output to extract metrics
        :param stdout: 
        :param stderr: 
        """
        pass


class ExecutionResult:

    def __init__(self):
        self.start = None
        self.duration = -1
        self.tool = None
        self.workload = None
        self.categories = None
        self.service_type = None
        self.metrics = None
        self.logs = None
        self.properties = {}
        self.provider = {}


class ExecutionError:

    def __init__(self):
        self.tool = None
        self.workload = None
        self.provider = None
        self.phase = None
        self.exception_type = None
        self.traceback = None
        self.exception_data = None
        self.timestamp = None



class ExecutionCommandInfo:
    """
    Basic information about the execution of a command
    """
    def __init__(self):
        self.started = None
        self.duration = None


class BenchmarkExecution:

    def __init__(self, benchmark, session):
        self.test = benchmark
        self.session = session
        self.id = str(uuid.uuid1())
        self.created = time.time()
        self.exec_env = None
        self.last_run_info = None

    def prepare(self) -> ExecutionCommandInfo:
        env_request = self.test.get_env_request()
        self.exec_env = self.session.get_execution_environment(env_request)
        logger.info('Using execution environment %s', str(self.exec_env))
        ret = ExecutionCommandInfo()
        ret.started = time.time()
        self.test.prepare(self)
        ret.duration = time.time() - ret.started
        return ret

    def execute(self, async=False) -> ExecutionCommandInfo:
        ret = ExecutionCommandInfo()
        ret.started = time.time()
        self.test.execute(self, async=async)
        ret.duration = time.time() - ret.started
        self.last_run_info = ret
        return ret

    def get_execution_result(self) -> ExecutionResult:
        if not self.last_run_info:
            return None

        e = ExecutionResult()
        e.start = self.last_run_info.started
        e.duration = self.test.get_runtime(self, 'run')
        e.tool = self.test.tool_id
        e.categories = self.test.workload_categories
        e.workload_description = self.test.workload_description
        e.workload = self.test.workload_id
        e.provider = self.session.provider.get_provder_properties_dict()
        e.exec_env = self.exec_env.get_specs_dict()
        stdout, stderr = self.test.get_result(self)
        e.logs = {'stdout': stdout, 'stderr': stderr}
        e.properties.update(self.session.props)
        e.metrics = {'duration': {'value': e.duration, 'unit': 's'}}
        if self.test.parser:
            try:
                e.metrics.update(self.test.parser.get_metrics(stdout, stderr))
            except Exception as ex:
                logger.error('Error parsing execution results: '.format(str(ex)))
        return e

    def collect_result(self):
        return self.test.get_result(self)

    def __str__(self) -> str:
        return '''
| Execution {0}
|  - test: {1} - {2}
|  - environment: {3}'''.format(self.id, self.test.tool_id, self.test.workload_id, self.exec_env)


class ExecutionEnvironment(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_specs_dict(self):
        """
        returns a dictionary with the specifications of the execution environment. It is used to get the data to store
        in the db.
        """
        pass

class ExecutionEnvironmentRequest:

    def __init__(self):
        pass


