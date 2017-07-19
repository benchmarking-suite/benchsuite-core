#!/usr/bin/env python
# BenchmarkingSuite - Benchmarking Controller
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
from appdirs import user_data_dir, site_config_dir, user_config_dir

from benchsuite.core.controller import BenchmarkingController

if __name__ == '__main__':

    c = BenchmarkingController(config_folder='/home/ggiammat/projects/ENG.CloudPerfect/workspace/testing/bsconfig')

    string = """
[provider]
class = benchsuite.stdlib.provider.existing_vm.ExistingVMProvider

[my_vm1]
ip_address = 217.172.12.215
key_path = /home/ggiammat/credentials/filab-vicenza/ggiammat-key.pem
user = ubuntu
platform = ubuntu
"""

    s = c.new_session_by_config_string(string)


    print(s)