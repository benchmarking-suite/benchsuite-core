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
from typing import Any

logger = logging.getLogger(__name__)

class BaseBenchmarkingSuiteException(Exception):
    pass

class UndefinedExecutionException(BaseBenchmarkingSuiteException):
    pass

class UndefinedSessionException(BaseBenchmarkingSuiteException):
    pass

class ControllerConfigurationException(BaseBenchmarkingSuiteException):
    pass

class BenchmarkConfigurationException(BaseBenchmarkingSuiteException):
    pass

class ProviderConfigurationException(BaseBenchmarkingSuiteException):
    pass


# TODO: this type of error should go in stdlib. Here we need a more generic exception
class BashCommandExecutionFailedException(BaseBenchmarkingSuiteException):

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.cmd = None
        self.exit_status = None
        self.stdout = None
        self.stderr = None


class NoExecuteCommandsFound(BaseBenchmarkingSuiteException):
    pass

def dump_BashCommandExecution_exception(e, dump_file):
    with open(dump_file, "w") as text_file:
        text_file.write("========== CMD ==========\n")
        text_file.write(e.cmd)
        text_file.write('\n\n>>> Exit status was {0}\n'.format(e.exit_status))
        text_file.write("\n\n========== STDOUT ==========\n")
        text_file.write(e.stdout)
        text_file.write("\n\n========== STDERR ==========\n")
        text_file.write(e.stderr)
        logger.info('Command stdout and stderr have been dumped to {0}'.format(dump_file))

