# Copyright 2016 Midokura SARL
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

from zephyr.common import cli
from zephyr.common import exceptions
from zephyr.vtm.underlay import overlay_manager


class MidonetOverlay(overlay_manager.OverlayManager):
    def plugin_iface(self, hv_host, iface, port_id):
        """
        :type hv_host:
        zephyr.vtm.underlay.direct_underlay_host.DirectUnderlayHost
        :type iface: str
        :type port: str
        """
        hv_host.execute(
            'mm-ctl --bind-port ' + str(port_id) + ' ' + str(iface))

    def unplug_iface(self, hv_host, port_id):
        """
        :type hv_host:
        zephyr.vtm.underlay.direct_underlay_host.DirectUnderlayHost
        :type iface: str
        :type port: str
        """
        hv_host.execute(
            'mm-ctl --unbind-port ' + str(port_id))
