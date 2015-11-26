#!/usr/bin/env python
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

from common.EchoServer import EchoServer, DEFAULT_ECHO_PORT
from common.CLI import LinuxCLI

import getopt
import sys
import threading

import signal

arg_map, _ = getopt.getopt(sys.argv[1:], 'i:p:d:')

ip = 'localhost'
port = DEFAULT_ECHO_PORT
data = "pong"

for arg, value in arg_map:
    if arg in ('-i'):
        ip = value
    elif arg in ('-p'):
        port = int(value)
    elif arg in ('-d'):
        data = value

tmp_status_file_name = '/tmp/echo-server-status.' + str(port)

stop_event = threading.Event()
stop_event.clear()

es = EchoServer(ip, port, data)

def term_handler(signum, frame):
    print "Exiting..."
    LinuxCLI().cmd("echo 'TERM: Stopping' >> " + tmp_status_file_name)
    stop_event.set()
    LinuxCLI().cmd("echo 'TERM: Exiting' >> " + tmp_status_file_name)
    exit(0)

signal.signal(signal.SIGTERM, term_handler)
LinuxCLI().cmd("echo 'Starting' > " + tmp_status_file_name)

try:
    es.start()
    running = True
    while running:
        stop_event.wait()
    LinuxCLI().cmd("echo 'Stopping' >> " + tmp_status_file_name)
    es.stop()
    LinuxCLI().cmd("echo 'Exiting' >> " + tmp_status_file_name)
except Exception as e:
    print "ERROR: " + str(e)
    LinuxCLI().cmd("echo 'ERROR: " + str(e) + "' >> " + tmp_status_file_name)
    exit(2)

exit(0)
