from distutils.core import setup

from setuptools import find_packages

setup(
    name='benchsuite.core',
    version='2.0.0-dev12',
    packages=find_packages('src'),
    namespace_packages=['benchsuite'],
    package_dir={'': 'src'},
    url='https://github.com/benchmarking-suite/benchsuite-common',
    license='',
    author='Gabriele Giammatteo',
    author_email='gabriele.giammatteo@eng.it',
    description='',
    install_requires=['appdirs']
)
