# Copyright 2015 Midokura SARL
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

import datetime
import logging
from zephyr.common import zephyr_constants
from zephyr_ptm.ptm import ptm_constants

APPLICATION_TYPE_UNKNOWN = 0
APPLICATION_TYPE_NETWORK_OVERLAY = 1
APPLICATION_TYPE_HYPERVISOR = 2
APPLICATION_TYPE_NSDB = 3
APPLICATION_TYPE_API = 4
APPLICATION_TYPE_RESOURCE_RETRIEVAL = 5
APPLICATION_TYPE_SUPPLEMENTARY = 6
APPLICATION_TYPE_ALL = [APPLICATION_TYPE_UNKNOWN,
                        APPLICATION_TYPE_NETWORK_OVERLAY,
                        APPLICATION_TYPE_HYPERVISOR,
                        APPLICATION_TYPE_NSDB,
                        APPLICATION_TYPE_API,
                        APPLICATION_TYPE_RESOURCE_RETRIEVAL,
                        APPLICATION_TYPE_SUPPLEMENTARY]
APPLICATION_MULTI_ALLOWED = [APPLICATION_TYPE_RESOURCE_RETRIEVAL,
                             APPLICATION_TYPE_SUPPLEMENTARY]


class Application(object):
    @staticmethod
    def get_name():
        return '<unknown>'

    @staticmethod
    def get_type():
        return APPLICATION_TYPE_UNKNOWN

    @staticmethod
    def type_as_str(app_type):
        if app_type == APPLICATION_TYPE_UNKNOWN:
            return "Unknown"
        if app_type == APPLICATION_TYPE_NETWORK_OVERLAY:
            return "Network-Overlay"
        if app_type == APPLICATION_TYPE_HYPERVISOR:
            return "Hypervisor-Service"
        if app_type == APPLICATION_TYPE_NSDB:
            return "NSDB"
        if app_type == APPLICATION_TYPE_API:
            return "API"
        if app_type == APPLICATION_TYPE_RESOURCE_RETRIEVAL:
            return "Resource Retrieval"
        if app_type == APPLICATION_TYPE_SUPPLEMENTARY:
            return "Supplementary-Application"

    def __init__(self, host, app_id=''):
        """
        :type host: Host
        :type app_id: str
        :return:
        """
        self.host = host
        """ :type: zephyr_ptm.ptm.host.host.Host"""
        self.cli = host.cli
        """ :type: LinuxCLI"""

        self.log_manager = self.host.log_manager
        self.LOG = logging.getLogger('ptm-null-root')
        """ :type: logging.Logger"""
        self.name = self.get_name()
        self.debug = False
        """ :type bool"""
        self.log_level = logging.INFO
        self.unique_id = app_id
        self.log_file_name = zephyr_constants.ZEPHYR_LOG_FILE_NAME

    def configure(self, host_cfg, app_config):
        pass

    def get_application_settings(self):
        return {}

    def get_resource(self, resource_name, **kwargs):
        """
        :type resource_name: str
        :rtype: any
        """
        return None

    def configure_logging(self,
                          log_file_name, debug=False):
        self.log_level = logging.DEBUG if debug is True else logging.INFO
        self.debug = debug
        self.log_file_name = log_file_name
        msec = int(datetime.datetime.utcnow().microsecond / 1000)
        logname = (self.name + '.' +
                   datetime.datetime.utcnow().strftime('%H%M%S') +
                   '.' + str(msec))

        if debug is True:
            self.LOG = self.log_manager.add_tee_logger(
                file_name=log_file_name,
                name=logname + '-debug',
                file_log_level=self.log_level,
                stdout_log_level=self.log_level)
            self.LOG.info("Turning on debug logs")
        else:
            self.LOG = self.log_manager.add_file_logger(
                file_name=log_file_name,
                name=logname,
                log_level=self.log_level)

    def print_config(self, indent=0):
        print(('    ' * indent) + self.name + ': Impl class ' +
              self.__class__.__name__)
        print(('    ' * (indent + 1)) + 'UUID: ' + str(self.unique_id))

    def prepare_config(self, log_manager):
        pass

    def create_cfg_map(self):
        return {}

    def create_app_cfg_map_for_process_control(self):
        ret = {
            'log_file_name': self.log_file_name,
            'class': self.__module__ + "." + self.__class__.__name__}
        ret.update(self.create_cfg_map())
        return ret

    def config_app_for_process_control(self, cfg_map):
        pass

    def wait_for_process_start(self):
        pass

    def wait_for_process_stop(self):
        pass

    def control_start(self):
        pass

    def control_stop(self):
        pass

    def prepare_environment(self):
        pass

    def cleanup_environment(self):
        pass
