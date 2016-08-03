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

from tests.midonet.upgrade import upgrade_standard_ptm
from tests.midonet.upgrade import upgrade_test_base

STANDARD_PTM_ROOT = '/tmp'
STANDARD_PTM_NAME = 'standard-ptm.mysql'
STANDARD_PTM_MYSQL_USER = 'root'
STANDARD_PTM_MYSQL_PASS = 'cat'
STANDARD_PTM_ZK_SERVER = 'zoo1'


class TestUpgradeTo50(upgrade_test_base.UpgradeTestBase):
    def test_standard_ptm(self):
        zk_ip = self.vtm.get_host(STANDARD_PTM_ZK_SERVER).get_ip()

        upgrade_standard_ptm.UnderlayStandardPTM._prepare_class(
            self.vtm, self.LOG)

        topo_module = upgrade_standard_ptm.UnderlayStandardPTM()

        self.load_zk_mysql_data(base_name=STANDARD_PTM_NAME,
                                zkserver=zk_ip + ':2181',
                                mysql_user=STANDARD_PTM_MYSQL_USER,
                                mysql_pass=STANDARD_PTM_MYSQL_PASS,
                                root_dir=STANDARD_PTM_ROOT)

        self.upgrade_test_main_flow(topo_module, new_version='5.0')
