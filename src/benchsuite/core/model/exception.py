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


from typing import Any


class UndefinedExecutionException(Exception):
    pass

class UndefinedSessionException(Exception):
    pass

class ControllerConfigurationException(Exception):
    pass

class BenchmarkConfigurationException(Exception):
    pass

class ProviderConfigurationException(Exception):
    pass

class BashCommandExecutionFailedException(Exception):

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.cmd = None
        self.exit_status = None
        self.stdout = None
        self.stderr = None
