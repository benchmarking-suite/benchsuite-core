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

class CloudService:

    def __init__(self, provider):
        self.provider = provider


class ComputeService(CloudService):

    post_create_script = 'echo "Hello World!"'

    def __init__(self, provider, image, size, vms_key, vms_privkey, vm_user, vm_platform, working_dir=None):
        CloudService.__init__(self, provider)
        self.image = image
        self.size = size
        self.keypair = vms_key
        self.privkey = vms_privkey
        self.vm_user = vm_user
        self.vm_platform = vm_platform
        self.working_dir = working_dir or '/home/' + self.vm_user


class CloudProvider:

    def __init__(self, type, endpoint, username, password, additional_params = None):
        self.type = type
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.additional_params = additional_params or {}



class TargetEnvironment:
    pass


class TargetEnvironmentManager:

    def __json__(self):
        return {'name': 'ciao'}


class BenchmarkingTest:

    def __init__(self, tool, workload):
        self.tool = tool
        self.workload = workload

class TestExecutor:
    pass