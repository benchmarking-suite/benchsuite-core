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
from abc import ABC

import logging

logger = logging.getLogger(__name__)


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

    def prepare(self) -> ExecutionCommandInfo:
        env_request = self.test.get_env_request()
        self.exec_env = self.session.get_execution_environment(env_request)
        logger.debug('Execution environment obtained %s', str(self.exec_env))
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
        return ret

    def collect_result(self):
        return self.test.get_result(self)

    def __str__(self) -> str:
        return '''
| Execution {0}
|  - test: {1} - {2}
|  - environment: {3}'''.format(self.id, self.test.name, self.test.workload, self.exec_env)


class ExecutionEnvironment(ABC):

    def __init__(self):
        pass


class ExecutionEnvironmentRequest:

    def __init__(self):
        pass


