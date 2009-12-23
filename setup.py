# -*- encoding:utf-8 -*-
# Copyright 2009 Atommica. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The setup and build script for the krdf library.
"""

from setuptools import setup

setup(
    name = "krdf",
    version = "0.0.1",
    url = 'http://github.com/krl/krdf',
    license = 'GNU GPL v3 or later',
    description='An RDF persistance layer on top of Pyrant',
    author = 'Kristoffer Ström',
    author_email = 'kristoffer@rymdkoloni.se',
    packages = ['krdf'],
    install_requires = ['setuptools', 'bsddb3'],
    include_package_data = True,
    classifiers = [
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Topic :: Database :: Front-Ends',
    ],
)
