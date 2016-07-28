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

from midonetclient.api import MidonetApi

from tests.neutron.features.lbaas.lbaas_test_utils import DEFAULT_POOL_PORT
from tests.neutron.features.lbaas.lbaas_test_utils import LBaaSTestCase
from zephyr.midonet import mn_install as mi
from zephyr.midonet import mn_upgrade as mu
from zephyr_ptm.ptm.config import version_config as vc


class UpgradeTestBase(LBaaSTestCase):
    def __init__(self, method_name='runTest'):
        super(UpgradeTestBase, self).__init__(method_name=method_name)
        self.vm_lbass_member_pool_a_b = None
        self.vm_lbass_member_pool_a = None
        self.vm_lbass_pinger = None
        self.vm_mn_lbaas_member_pool_mn_neutron_c = None
        self.vm_mn_lbaas_member_pool_mn = None
        self.vm_main_net_with_fip = None
        self.vm_main_net_private = None
        self.vm_new1_net_with_fip = None
        self.vm_new1_net_private = None
        self.vm_new2_net_with_fip = None
        self.vm_new2_net_private = None

        self.neutron_bridge_to_modify = None
        self.neutron_router_to_modify = None
        self.neutron_port_to_modify = None
        self.neutron_sg_to_modify = None

        self.mn_uri = vc.ConfigMap.get_configured_parameter(
            'param_midonet_api_url')
        self.mn_api = MidonetApi(self.mn_uri, 'admin', 'cat', 'admin')
        """ :type: midonetclient.api.MidonetApi """

    def setup_basic_neutron_topology(self):
        self.neutron_sg_to_modify = self.create_security_group(
            name='test_sg')

        self.create_port('sg_port_test',
                         self.main_network['id'],
                         sg_ids=[self.neutron_sg_to_modify['id']])

        net1 = self.create_network(name='new1_net')
        sub1 = self.create_subnet(name='new1_sub', net_id=net1['id'],
                                  cidr='10.100.100.0/24')

        self.neutron_bridge_to_modify = self.create_network(
            name='new2_net')
        sub2 = self.create_subnet(
            name='new2_sub',
            net_id=self.neutron_bridge_to_modify['id'],
            cidr='10.100.101.0/24')

        self.neutron_router_to_modify = self.create_router(
            name='new1_new2_router',
            pub_net_id=self.pub_network['id'],
            priv_sub_ids=[sub1['id'], sub2['id']])

        port1, self.vm_main_net_with_fip, _ = self.create_vm_server(
            'vm_main1', net_id=self.main_network['id'])

        _, self.vm_main_net_private, _ = self.create_vm_server(
            'vm_main2', net_id=self.main_network['id'])

        port3, self.vm_new1_net_with_fip, _ = self.create_vm_server(
            'vm_new1a', net_id=net1['id'])

        _, self.vm_new1_net_private, _ = self.create_vm_server(
            'vm_new1b', net_id=net1['id'])

        port5, self.vm_new2_net_with_fip, _ = self.create_vm_server(
            'vm_new2a', net_id=self.neutron_bridge_to_modify['id'])

        self.neutron_port_to_modify, self.vm_new2_net_private, _ = (
            self.create_vm_server(
                'vm_new2b', net_id=self.neutron_bridge_to_modify['id']))

        self.create_floating_ip(self.pub_network['id'], port_id=port1['id'])
        self.create_floating_ip(self.pub_network['id'], port_id=port3['id'])
        self.create_floating_ip(self.pub_network['id'], port_id=port5['id'])

    def setup_midonet_topology(self):
        # Create a new MidoNet bridge to upgrade
        new_br = (self.mn_api.add_bridge()
                  .tenant_id('admin')
                  .name('mn_br_test')
                  .disable_anti_spoof(True)
                  .create())
        """ :type: midonetclient.bridge.Bridge"""

        # Create a new MidoNet DHCP to upgrade
        (new_br.add_dhcp_subnet()
         .default_gateway('10.200.200.1')
         .subnet_prefix('10.200.200.0')
         .subnet_length(24)
         .enabled(True)
         .create())
        """ :type: midonetclient.dhcp_subnet.DhcpSubnet"""

        # Create a new MidoNet bridge port to upgrade
        br_port = (new_br.add_port()
                   .create())
        """ :type: midonetclient.port.Port"""

        new_br.disable_anti_spoof(True)

        # Create a new MidoNet router to upgrade
        new_rtr = (self.mn_api.add_router()
                   .name('mn_rtr_test')
                   .tenant_id('admin')
                   .create())
        """ :type: midonetclient.router.Router"""

        # Create a new MidoNet router port to upgrade (and link to bridge)
        rtr_port = (new_rtr.add_port()
                    .port_address('10.200.200.1')
                    .network_address('10.200.200.0')
                    .network_length(24)
                    .port_mac("AA:BB:CC:DD:EE:FF")
                    .create())
        """ :type: midonetclient.port.Port"""

        br_port.link(rtr_port.get_id())

        # Create MidoNet port groups to upgrade
        pg = (self.mn_api.add_port_group()
              .tenant_id('admin')
              .name('pg-test')
              .stateful(True)
              .create())
        """ :type: midonetclient.port_group.PortGroup"""

        (pg.add_port_group_port()
         .port_id(br_port.get_id())
         .create())

        # Create MidoNet chains to upgrade
        new_chain_obj = (self.mn_api.add_chain()
                         .tenant_id('admin')
                         .name("test_chain")
                         .create())
        """ :type: midonetclient.chain.Chain"""

        new_chain2_obj = (self.mn_api.add_chain()
                          .tenant_id('admin')
                          .name("test2_chain")
                          .create())
        """ :type: midonetclient.chain.Chain"""

        new_chain2_obj.add_rule().type("accept").create()
        new_chain_obj.add_rule().type("accept").create()
        new_chain_obj.add_rule().type("jump").create()

    def setup_neutron_lbaas(self):
        if 'lbaas' not in self.api_extension_map:
            return

        self.create_member_net(name='main')
        self.create_lbaas_net(name='main')
        self.create_pinger_net(name='main')
        self.create_lb_router(name='main',
                              gw_net_id=self.pub_network['id'])

        self.create_lbaas_net(name='main2',
                              cidr='192.168.122.0/24')
        self.create_lb_router(name='main2',
                              gw_net_id=self.pub_network['id'])

        poola = self.create_pool(
            subnet_id=self.topos['main']['lbaas']['subnet']['id'])
        poolb = self.create_pool(
            subnet_id=self.topos['main2']['lbaas']['subnet']['id'])

        self.create_vip(subnet_id=self.pub_subnet['id'],
                        protocol_port=DEFAULT_POOL_PORT,
                        name='poola-vip1',
                        pool_id=poola['id'])

        self.create_vip(subnet_id=self.pub_subnet['id'],
                        protocol_port=DEFAULT_POOL_PORT + 1,
                        name='poolb-vip1',
                        pool_id=poolb['id'])

        vms = self.create_member_vms(num_members=2)
        self.vm_lbass_member1 = vms[0]
        self.vm_lbass_member2 = vms[1]

        self.vm_lbass_pinger = self.create_pinger_vm()

        self.create_member(pool_id=poola['id'],
                           ip_addr=self.vm_lbass_member1.ip)
        self.create_member(pool_id=poola['id'],
                           ip_addr=self.vm_lbass_member2.ip)

        self.create_member(pool_id=poolb['id'],
                           ip_addr=self.vm_lbass_member1.ip)

        self.create_health_monitor()

        hm1 = self.create_health_monitor()
        self.associate_health_monitor(hm1['id'], poola['id'])

        hm2 = self.create_health_monitor()
        self.associate_health_monitor(hm2['id'], poolb['id'])

        self.create_floating_ip(
            pub_net_id=self.pub_network['id'],
            port_id=self.vm_lbass_pinger.port['id'])

    def setup_midonet_lbaas(self):

        lbaas_rtr = (self.mn_api
                     .add_router()
                     .name('mn_lbaas_test')
                     .tenant_id('admin')
                     .create())
        """ :type: midonetclient.router.Router"""

        lb_obj = (self.mn_api.add_load_balancer()
                  .create())
        """ :type: midonetclient.load_balancer.LoadBalancer"""

        lbaas_rtr.load_balancer_id(lb_obj.get_id()).update()

        pool_obj = (lb_obj.add_pool()
                    .lb_method("ROUND_ROBIN")
                    .protocol("TCP")
                    .create())
        """ :type: midonetclient.pool.Pool"""

        vms = self.create_member_vms(num_members=2)
        self.vm_mn_lbaas_member_pool_mn = vms[0]
        self.vm_mn_lbaas_member_pool_mn_neutron_c = vms[1]

        (pool_obj.add_pool_member()
         .address(self.vm_mn_lbaas_member_pool_mn.ip)
         .protocol_port(5081)
         .create())
        (pool_obj.add_pool_member()
         .address(self.vm_mn_lbaas_member_pool_mn_neutron_c.ip)
         .protocol_port(5081)
         .create())
        (pool_obj.add_vip()
         .address("200.200.0.59")
         .protocol_port(5081)
         .create())

    def setup_edge_rotuer_and_bgp(self):
        rtrs = self.mn_api.get_routers(query=None)
        pr = next(r
                  for r in rtrs
                  if r.get_name() == "MidoNet Provider Router")
        """ :type: midonetclient.router.Router """
        rport = (pr.add_port()
                 .port_address('172.16.2.2')
                 .network_address('172.16.2.0')
                 .network_length(24)
                 .create())
        """ :type: midonetclient.port.Port """

        hosts = self.mn_api.get_hosts()
        edge_host = next(h
                         for h in hosts
                         if h.get_name() == "edge1")
        """ :type: midonetclient.host.Host """

        self.mn_api.add_host_interface_port(edge_host, rport.get_id(), 'eth1')

        (pr.add_route()
         .type('normal')
         .weight(100)
         .next_hop_gateway('172.16.2.1')
         .next_hop_port(rport.get_id())
         .dst_network_addr('0.0.0.0')
         .dst_network_length(0)
         .src_network_addr('0.0.0.0')
         .src_network_length(0)
         .create())

        pr_bgp = (rport.add_bgp()
                  .peer_addr('172.16.2.1')
                  .peer_as('54321')
                  .local_as('12345')
                  .create())

        (pr_bgp.add_ad_route()
         .nw_prefix('200.200.0.0')
         .nw_prefix_length(24)
         .create())

        rtr_bgp_port1 = (pr.add_port()
                         .port_address('10.200.200.5')
                         .network_address('10.200.200.0')
                         .network_length(24)
                         .port_mac("BB:CC:DD:EE:FF:00")
                         .create())
        """ :type: midonetclient.port.Port"""

        rtr_bgp_port2 = (pr.add_port()
                         .port_address('10.200.200.6')
                         .network_address('10.200.200.0')
                         .network_length(24)
                         .port_mac("CC:DD:EE:FF:00:11")
                         .create())
        """ :type: midonetclient.port.Port"""

        tr_bgp1 = (rtr_bgp_port1.add_bgp()
                   .peer_addr('172.16.2.1')
                   .peer_as('23456')
                   .local_as('65432')
                   .create())
        (tr_bgp1.add_ad_route()
         .nw_prefix('10.200.200.0')
         .nw_prefix_length(24)
         .create())

        tr_bgp2 = (rtr_bgp_port1.add_bgp()
                   .peer_addr('172.16.3.1')
                   .peer_as('34567')
                   .local_as('76543')
                   .create())
        (tr_bgp2.add_ad_route()
         .nw_prefix('10.200.201.0')
         .nw_prefix_length(24)
         .create())

        tr_bgp3 = (rtr_bgp_port2.add_bgp()
                   .peer_addr('172.16.3.1')
                   .peer_as('34567')
                   .local_as('76543')
                   .create())
        (tr_bgp3.add_ad_route()
         .nw_prefix('10.200.201.0')
         .nw_prefix_length(24)
         .create())

    def modify_neutron_topology_with_midonet(self):
        # Create a Midonet bridge port on a Neutron network
        bridges = self.mn_api.get_bridges(query=None)
        neutron_br = next(b
                          for b in bridges
                          if b.get_name() == "new2_net")
        """ :type: midonetclient.bridge.Bridge"""

        if neutron_br:
            (neutron_br.add_port()
             .create())
            neutron_br.disable_anti_spoof(True).update()

        # Create a MidoNet router port on a Neutron router
        tr = next(r
                  for r in self.mn_api.get_routers(query=None)
                  if r.get_name() == "new1_new2_router")
        """ :type: midonetclient.router.Router"""

        (tr.add_port()
         .port_address('10.155.155.5')
         .network_address('10.155.155.0')
         .network_length(24)
         .port_mac("00:11:22:AA:BB:CC")
         .create())

        # Modify a Neutron network with MidoNet API
        # Modify a Neutron router with MidoNet API
        # Modify a Neutron port with MidoNet API
        # Modify a Neutron SG (chains) with MidoNet API

        # Modify a Netron LBAAS with MidoNet API
        neutron_lb_rtr_id = self.topos['main']['router']['id']
        neutron_lb_rtr = self.mn_api.get_router(neutron_lb_rtr_id)
        neutron_lb = self.mn_api.get_load_balancer(
            neutron_lb_rtr.get_load_balancer_id())
        neutron_c_pool = (neutron_lb
                          .add_pool()
                          .lb_method("ROUND_ROBIN")
                          .protocol("TCP")
                          .create())
        """ :type: midonetclient.pool.Pool"""

        (neutron_c_pool.add_pool_member()
         .address(self.vm_mn_lbaas_member_pool_mn_neutron_c.ip)
         .protocol_port(5082)
         .create())
        (neutron_c_pool.add_vip()
         .address("200.200.0.61")
         .protocol_port(5082)
         .create())

    def check_neutron_topology(self):
        self.api.get_network()

    def check_midonet_topology(self):
        pass

    def check_bgp(self):
        pass

    def check_midonet_vm_communication(self):
        pass

    def check_neutron_vm_communication(self):
        pass

    def check_neutron_lbaas(self):
        pass

    def check_midonet_lbaas(self):
        pass

    def do_upgrade_to_X(self, new_version):
        upgrader = mu.DataMigration(debug=True,
                                    log_manager=self.vtm.log_manager)
        upgrader.prepare()
        upgrader.migrate()
        upgrader.provider_router_to_edge_router()
        upgrader.midonet_antispoof_to_allowed_address_pairs()
        upgrader.midonet_routes_to_extra_routes()

        # TODO(micucci) - Do the upgrade here
        import pdb
        pdb.set_trace()

        installer = mi.MidonetInstaller(
            version=new_version,
            debug=True)

        installer.install()

        # TODO(micucci) - Restart all the midolman servers with new version
        # and new topo
