__author__ = 'micucci'

import unittest
from VTM.VirtualTopologyConfig import VirtualTopologyConfig

class MockClient():
    def __init__(self, *args, **kwargs):
        self.subnet = {}
        self.options = {}
        if kwargs is not None:
            for k, v in kwargs.iteritems():
                self.options[k] = v
        pass

    def list_ports(self):
        pass

    def list_networks(self):
        pass

    def delete_port(self, port):
        pass

    def delete_network(self, network):
        pass

    def set_subnet(self, subnet):
        self.subnet = subnet

    def show_subnet(self):
        return self.subnet

    def get_option(self, key):
        if key in self.options:
            return self.options[key]
        return None


class VirtualTopologyConfigUnitTest(unittest.TestCase):
    def test_creation(self):
        api = VirtualTopologyConfig(MockClient, endpoint_url='test', auth_strategy='test2', option1='test3')

        self.assertEqual(api.get_client().get_option('endpoint_url'), 'test')
        self.assertEqual(api.get_client().get_option('auth_strategy'), 'test2')
        self.assertEqual(api.get_client().get_option('option1'), 'test3')

    def test_subnet(self):
        api = VirtualTopologyConfig(MockClient)
        subnet =  {'subnet': {
            'name': 'test-l2',
            'enable_dhcp': True,
            'network_id': 'b6c86193-024c-4aeb-bd9c-ffc747bb8a74',
            'tenant_id': 'mdts2-ft2015-03-10 06:03:17',
            'dns_nameservers': [],
            'ipv6_ra_mode': None,
            'allocation_pools': [{
                                     'start': '1.1.1.2',
                                     'end': '1.1.1.254'}],
            'gateway_ip': '1.1.1.1',
            'ipv6_address_mode': None,
            'ip_version': 4,
            'host_routes': [],
            'cidr': '1.1.1.0/24',
            'id': '6c838ffc-6a40-49ba-b363-6380b0a7dae6'}}

        api.get_client().set_subnet(subnet)
        self.assertEqual(api.get_client().show_subnet(), subnet)



if __name__ == '__main__':
    unittest.main()
