#!/usr/bin/env python
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

import sys

from common.Exceptions import *
from PTM.PhysicalTopologyManager import PhysicalTopologyManager, CONTROL_CMD_NAME
from common.CLI import LinuxCLI
from CBT.EnvSetup import EnvSetup
import traceback

def usage(exceptClass):
    print 'Usage: ' + CONTROL_CMD_NAME + ' {startup|shutdown|config} [options]'
    print 'Usage: ' + CONTROL_CMD_NAME + ' neutron {install} [options]'
    if exceptClass is not None:
        raise exceptClass()

try:

    if len(sys.argv) < 2:
        usage(ExitCleanException)
    else:
        cmd = sys.argv[1]

        config_file = 'config.json'

        root_dir = LinuxCLI().cmd('pwd').strip()

        print "Setting root dir to: " + root_dir
        ptm = PhysicalTopologyManager(root_dir=root_dir, log_root_dir='./tmp/logs')

        ptm.configure(config_file)

        if cmd == 'neutron':
            if len(sys.argv) < 3:
                usage(ExitCleanException)
            if sys.argv[2] == 'install':
                EnvSetup.install_neutron_client()
        elif cmd == 'startup':
            ptm.startup()
        elif cmd == 'shutdown':
            ptm.shutdown()
        elif cmd == 'config':
            ptm.print_config()
        else:
            raise ArgMismatchException(' '.join(sys.argv[1:]))
   
except ExitCleanException:
    exit(1)
except ArgMismatchException as a:
    print 'Argument mismatch: ' + str(a)
    usage(None)
    traceback.print_tb(sys.exc_traceback)
    exit(2)
except ObjectNotFoundException as e:
    print 'Object not found: ' + str(e)
    traceback.print_tb(sys.exc_traceback)
    exit(2)
except SubprocessFailedException as e:
    print 'Subprocess failed to execute: ' + str(e)
    traceback.print_tb(sys.exc_traceback)
    exit(2)
except TestException as e:
    print 'Unknown exception: ' + str(e)
    traceback.print_tb(sys.exc_traceback)
    exit(2)
