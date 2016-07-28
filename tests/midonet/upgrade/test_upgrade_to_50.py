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

from tests.midonet.upgrade import upgrade_test_base


class TestUpgradeTo50(upgrade_test_base.UpgradeTestBase):
    def test_upgrade(self):
        # Setup topology
        self.setup_basic_neutron_topology()
        self.setup_neutron_lbaas()
        self.setup_midonet_topology()
        self.setup_midonet_lbaas()
        self.setup_edge_rotuer_and_bgp()

        # Do the upgrade here
        self.do_upgrade_to_X(new_version="5.0")

        # Test upgraded topology
        self.check_neutron_topology()
        self.check_midonet_topology()
        self.check_neutron_lbaas()
        self.check_midonet_lbaas()
        self.check_bgp()
        self.check_neutron_vm_communication()
        self.check_midonet_vm_communication()
