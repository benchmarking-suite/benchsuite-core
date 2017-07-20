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

from benchsuite.core.model.execution import BenchmarkExecution
from benchsuite.core.model.provider import ServiceProvider


class BenchmarkingSession:

    def __init__(self, provider: ServiceProvider):
        self.provider = provider
        self.id = str(uuid.uuid1())
        self.created = time.time()
        self.executions = {}

    def new_execution(self, benchmark):
        e = BenchmarkExecution(benchmark, self)
        self.executions[e.id] = e
        return e

    def list_executions(self):
        return self.executions.values()

    def get_execution(self, exec_id):
        return self.executions[exec_id]

    def get_execution_environment(self, request):
        return self.provider.get_execution_environment(request)

    def destroy(self):
        self.provider.destroy_service()