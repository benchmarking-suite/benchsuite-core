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
import os
import pickle

from benchsuite.core.model.exception import UndefinedSessionException



logger = logging.getLogger(__name__)

DEFAULT_STORAGE_SESSIONS_FILE = 'sessions.dat'

class SessionStorageManager:

    def __init__(self, folder):
        self.storage_file = folder + os.path.sep + DEFAULT_STORAGE_SESSIONS_FILE
        self.sessions = {}

    def load(self):
        try:
            self.sessions = pickle.load( open( self.storage_file, "rb"))
            logger.debug('Benchmarking Sessions loaded from %s (%d sessions)', self.storage_file, len(self.sessions))

        except FileNotFoundError:
            logger.debug('Benchmarking Sessions storage file does not exit (%s) (Not loading sessions)', self.storage_file)


    def store(self):
        pickle.dump(self.sessions, open(self.storage_file, "wb"))
        logger.debug('Benchmarking Sessions stored to %s (%d sessions)', self.storage_file, len(self.sessions))

    def list(self):
        return self.sessions.values()

    def get(self, session_id):
        if session_id not in self.sessions:
            raise UndefinedSessionException('The session with id={0} does not exist'.format(session_id))

        return self.sessions[session_id]

    def add(self, session):
        self.sessions[session.id] = session

    def remove(self, session):
        del self.sessions[session.id]