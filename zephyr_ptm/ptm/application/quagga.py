# Copyright 2015 Midokura SARL
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

from configuration_handler import FileConfigurationHandler
from os import path
from zephyr.common.file_location import *
from zephyr_ptm.ptm.application import application


class Quagga(application.Application):

    def __init__(self, host, app_id=''):
        super(Quagga, self).__init__(host, app_id)
        self.num_id = '1'
        self.configurator = RouterFileConfiguration()

    @staticmethod
    def get_type():
        return application.APPLICATION_TYPE_SUPPLEMENTARY

    def configure(self, host_cfg, app_cfg):
        """
        Configure this host type from a PTC HostDef config and the
        app-specific configuration
        :type host_cfg: HostDef
        :type app_cfg: ApplicationDef
        :return:
        """
        if 'id' in app_cfg.kwargs:
            self.num_id = app_cfg.kwargs['id']

        log_dir = '/var/log/quagga.' + self.num_id
        self.host.log_manager.add_external_log_file(
            FileLocation(log_dir + '/bgpd.log'), self.num_id,
            '%Y/%m/%d %H:%M:%S')
        self.host.log_manager.add_external_log_file(
            FileLocation(log_dir + '/zebra.log'), self.num_id,
            '%Y/%m/%d %H:%M:%S')

    def prepare_config(self, log_manager):
        self.configurator.configure(self.num_id)

    def create_cfg_map(self):
        return {'num_id': self.num_id}

    def config_app_for_process_control(self, cfg_map):
        self.num_id = cfg_map['num_id']

    def wait_for_process_start(self):
        pass

    def prepare_environment(self):
        self.configurator.mount_config(self.num_id)

    def cleanup_environment(self):
        self.configurator.unmount_config()

    def control_start(self):
        self.host.run_app_command('/etc/init.d/quagga', self, 'start')
        if self.cli.exists('/etc/rc.d/init.d/bgpd'):
            self.host.run_app_command('/etc/rc.d/init.d/bgpd', self, 'start')

    def control_stop(self):
        self.host.run_app_command('/etc/init.d/quagga', self, 'stop')
        if self.cli.exists('/etc/rc.d/init.d/bgpd'):
            self.host.run_app_command('/etc/rc.d/init.d/bgpd', self, 'stop')


class RouterFileConfiguration(FileConfigurationHandler):
    def __init__(self):
        super(RouterFileConfiguration, self).__init__()

    def configure(self, num_id):
        etc_dir = '/etc/quagga.' + num_id
        var_lib_dir = '/var/lib/quagga.' + num_id
        var_log_dir = '/var/log/quagga.' + num_id
        var_run_dir = '/run/quagga.' + num_id
        this_dir = path.dirname(path.abspath(__file__))

        self.cli.rm(etc_dir)
        self.cli.rm(var_log_dir)
        self.cli.rm(var_lib_dir)
        self.cli.rm(var_run_dir)

        if not self.cli.exists(var_lib_dir):
            self.cli.mkdir(var_lib_dir)
            self.cli.chown(var_lib_dir, 'quagga', 'quagga')

        if not self.cli.exists(var_log_dir):
            self.cli.mkdir(var_log_dir)
            self.cli.chown(var_log_dir, 'quagga', 'quagga')

        self.cli.mkdir('/run/quagga')
        if not self.cli.exists(var_run_dir):
            self.cli.mkdir(var_run_dir)
            self.cli.chown(var_run_dir, 'quagga', 'quagga')

        if num_id == '1':
            self.cli.copy_dir(this_dir + '/scripts/quagga.1', etc_dir)
        else:
            # TODO(micucci): Make Quagga configure quagga correctly
            # for multiple routers
            """mmconf_file = mmetc_dir + '/midolman.conf'
            self.cli.copy_dir(
                this_dir + '/scripts/quagga.2+', etc_dir)
            self.cli.regex_file(
                mmconf_file,
                's/^\[midolman\]/\[midolman\]\\nbgp_keepalive=1/')
            self.cli.regex_file(
                mmconf_file,
                's/^\[midolman\]/\[midolman\]\\nbgp_holdtime=3/')
            self.cli.regex_file(
                mmconf_file,
                's/^\[midolman\]/\[midolman\]\\nbgp_connect_retry=1/')"""

    def mount_config(self, num_id):
        self.cli.mount('/run/quagga.' + num_id, '/run/quagga')
        self.cli.mount('/var/log/quagga.' + num_id, '/var/log/quagga')
        self.cli.mount('/etc/quagga.' + num_id, '/etc/quagga')

    def unmount_config(self):
        self.cli.unmount('/run/quagga')
        self.cli.unmount('/var/log/quagga')
        self.cli.unmount('/etc/quagga')
