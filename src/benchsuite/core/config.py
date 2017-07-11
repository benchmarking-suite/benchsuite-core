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



import os
from appdirs import user_data_dir


class ControllerConfiguration():

    CLOUD_PROVIDERS_DIR = 'providers'
    BENCHMARKS_DIR = 'benchmarks'

    def __init__(self, config_folder):
        self.root = config_folder

    def get_default_data_dir(self):
        d = user_data_dir('BenchmarkingSuite', None)
        if not os.path.exists(d):
            os.makedirs(d)
        return d

    def get_provider_config_file(self, name):
        return self.root + os.path.sep + self.CLOUD_PROVIDERS_DIR + os.path.sep + name + '.conf'

    def get_benchmark_config_file(self, name):
        return self.root + os.path.sep + self.BENCHMARKS_DIR + os.path.sep + name + '.conf'

