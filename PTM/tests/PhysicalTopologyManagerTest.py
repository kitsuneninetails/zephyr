__author__ = 'micucci'
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

import unittest

from PhysicalTopologyManager import PhysicalTopologyManager
from common.CLI import LinuxCLI

class PhysicalTopologyManagerTest(unittest.TestCase):

    def test_configure(self):
        ptm = PhysicalTopologyManager(root_dir='../..', log_root_dir='./test-logs')

        ptm.configure('./test-config.json')

        self.assertTrue('zoo1' in ptm.hosts_by_name)
        self.assertTrue('cass1' in ptm.hosts_by_name)
        self.assertTrue('edge1' in ptm.hosts_by_name)

        self.assertEqual(ptm.host_by_start_order[0].name, 'root')
        self.assertEqual(ptm.host_by_start_order[1].name, 'external1')
        self.assertEqual(ptm.host_by_start_order[2].name, 'test-host1')
        self.assertEqual(ptm.host_by_start_order[3].name, 'test-host2')
        self.assertEqual(ptm.host_by_start_order[4].name, 'edge1')
        self.assertEqual(ptm.host_by_start_order[5].name, 'zoo1')
        self.assertEqual(ptm.host_by_start_order[6].name, 'cass1')
        self.assertEqual(ptm.host_by_start_order[7].name, 'cmp1')

        zk_host = ptm.hosts_by_name['zoo1']

        self.assertTrue('eth0' in zk_host.interfaces)

        root_host = ptm.hosts_by_name['root']

        self.assertTrue('zoo1eth0' in root_host.interfaces)

    def test_print_config(self):
        ptm = PhysicalTopologyManager(root_dir='../..', log_root_dir='./test-logs')

        ptm.configure('./test-config.json')

        ptm.print_config()

    def test_boot(self):
        ptm = PhysicalTopologyManager(root_dir='../..', log_root_dir='./test-logs')

        ptm.configure('./test-config.json')

        for h in ptm.host_by_start_order:
            h.create()
        for h in ptm.host_by_start_order:
            h.boot()
        for h in ptm.host_by_start_order:
            h.net_up()
        for h in ptm.host_by_start_order:
            h.net_finalize()

        self.assertTrue(LinuxCLI().grep_cmd('ip netns', 'zoo1'))
        self.assertTrue(LinuxCLI().grep_cmd('ip netns', 'test-host1'))
        root_host = ptm.hosts_by_name['root']
        test_host1 = ptm.hosts_by_name['test-host1']

        self.assertTrue(root_host.cli.grep_cmd('ip l', 'th1eth1'))
        self.assertTrue(test_host1.cli.grep_cmd('ip l', 'eth1'))

        for h in reversed(ptm.host_by_start_order):
            h.net_down()
        for h in reversed(ptm.host_by_start_order):
            h.shutdown()
        for h in reversed(ptm.host_by_start_order):
            h.remove()

        self.assertFalse(LinuxCLI().grep_cmd('ip netns', 'zoo1'))
        self.assertFalse(LinuxCLI().grep_cmd('ip netns', 'test-host1'))

    def test_startup(self):
        ptm = PhysicalTopologyManager(root_dir='../..', log_root_dir='./test-logs')

        ptm.configure('./test-config.json')
        ptm.startup()

        self.assertTrue(LinuxCLI().grep_cmd('ip netns', 'zoo1'))
        self.assertTrue(LinuxCLI().grep_cmd('ip netns', 'test-host1'))
        root_host = ptm.hosts_by_name['root']
        test_host1 = ptm.hosts_by_name['test-host1']

        self.assertTrue(root_host.cli.grep_cmd('ip l', 'th1eth1'))
        self.assertTrue(test_host1.cli.grep_cmd('ip l', 'eth1'))

        ptm.shutdown()

        self.assertFalse(LinuxCLI().grep_cmd('ip netns', 'zoo1'))
        self.assertFalse(LinuxCLI().grep_cmd('ip netns', 'test-host1'))

    def tearDown(self):
        LinuxCLI().cmd('ip netns del cass1')
        LinuxCLI().cmd('ip netns del cmp1')
        LinuxCLI().cmd('ip netns del zoo1')
        LinuxCLI().cmd('ip netns del edge1')
        LinuxCLI().cmd('ip netns del external1')
        LinuxCLI().cmd('ip netns del test-host1')
        LinuxCLI().cmd('ip netns del test-host2')
        LinuxCLI().cmd('ip l set dev br0 down')
        LinuxCLI().cmd('ip l set dev brv0 down')
        LinuxCLI().cmd('ip l del zoo1eth0')
        LinuxCLI().cmd('ip l del cmp1eth0')
        LinuxCLI().cmd('ip l del cass1eth0')
        LinuxCLI().cmd('ip l del th1eth0')
        LinuxCLI().cmd('ip l del th1eth1')
        LinuxCLI().cmd('ip l del th2eth0')
        LinuxCLI().cmd('brctl delbr br0')
        LinuxCLI().cmd('brctl delbr brv0')


if __name__ == '__main__':
    unittest.main()