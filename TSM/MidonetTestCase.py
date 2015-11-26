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

import logging

from TestScenario import TestScenario
from TSM.TestCase import TestCase
from TSM.fixtures.MidonetTestFixture import MidonetTestFixture


class MidonetTestCase(TestCase):

    def __init__(self, methodName='runTest'):
        super(MidonetTestCase, self).__init__(methodName)
        self.midonet_fixture = None
        """:type: MidonetTestFixture"""
        self.api = None
        """ :type: MidonetApi"""

    @classmethod
    def _prepare_class(cls, current_scenario,
                       test_case_logger=logging.getLogger()):
        """
        :type current_scenario: TestScenario
        :type test_case_logger: logging.logger
        """
        super(MidonetTestCase, cls)._prepare_class(current_scenario, test_case_logger)

        # Only add the midonet-setup fixture once for each scenario.
        if 'midonet-setup' not in current_scenario.fixtures:
            test_case_logger.debug('Adding midonet-setup fixture for scenario: ' +
                                   type(current_scenario).__name__)
            midonet_fixture = MidonetTestFixture(cls.vtm, cls.ptm, current_scenario.LOG)
            current_scenario.add_fixture('midonet-setup', midonet_fixture)

    def run(self, result=None):
        """
        Special run override to make sure to set up neutron data prior to running
        the test case function.
        """
        self.midonet_fixture = self.current_scenario.get_fixture('midonet-setup')
        self.api = self.midonet_fixture.api
        super(MidonetTestCase, self).run(result)
