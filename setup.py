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

from distutils.core import setup
import os
from setuptools import find_packages

# import the VERSION from the source code
import sys
sys.path.append(os.getcwd() + '/src/benchsuite')
from core import VERSION


setup(
    name='benchsuite.core',
    version='.'.join(map(str, VERSION)),

    description='The core library of the Benchmarking Suite',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),

    url='https://github.com/benchmarking-suite/benchsuite-core',

    author='Gabriele Giammatteo',
    author_email='gabriele.giammatteo@eng.it',

    license='Apache',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: System :: Benchmark',
        'Topic :: Utilities',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
        'Operating System :: Unix'
    ],
    keywords='benchmarking cloud testing performance',

    packages=find_packages('src'),
    namespace_packages=['benchsuite'],
    package_dir={'': 'src'},

    install_requires=['appdirs']

)
