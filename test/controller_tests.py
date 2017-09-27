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

import logging

import sys

from benchsuite.core.controller import BenchmarkingController

if __name__ == '__main__':

    os.environ['BENCHSUITE_CONFIG_FOLDER'] = '/home/ggiammat/projects/ENG.CloudPerfect/workspace/testing/bsconfig'
    logging.basicConfig(level=logging.DEBUG)

    with BenchmarkingController() as bc:

        s = bc.new_session('amazon-us-west-1', 'ubuntu_14_micro')
        #s = bc.new_session('filab-vicenza', 'ubuntu_small')
        e = bc.new_execution(s.id, 'filebench', 'varmail_short')

        bc.prepare_execution(e.id)

        print('Done')
