#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021-2022 Bosch Rexroth AG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import time
import json
import ctrlxdatalayer
from ctrlxdatalayer.variant import Variant, Result
import pylogix
from pylogix import PLC

import pycomm3
from pycomm3 import LogixDriver

from helper.ctrlx_datalayer_helper import get_provider

from app.ab_provider_node_bulk import ABnode

def main():

    with ctrlxdatalayer.system.System("") as datalayer_system:
        datalayer_system.start(False)

        # ip="10.0.2.2", ssl_port=8443: ctrlX virtual with port forwarding and default port mapping
        provider, connection_string = get_provider(datalayer_system)
        if provider is None:
            print("ERROR Connecting", connection_string, "failed.", flush=True)
            sys.exit(1)

        with provider:  # provider.close() is called automatically when leaving with... block

            result = provider.start()
            if result != Result.OK:
                print("ERROR Starting Data Layer Provider failed with:", result, flush=True)
                return

            # Path to compiled files
            snap_path = os.getenv('SNAP')
            #if snap_path is None:
                # Debug environment
                #bfbs_path = os.path.join("./bfbs/", bfbs_file)
                #mddb_path = os.path.join("./mddb/", mddb_file)

            #else:
                # snap environment
                #bfbs_path = os.path.join(snap_path, bfbs_file)
                #mddb_path = os.path.join(snap_path, mddb_file)
            abProviderList = []
            comm = PLC()
            devices = comm.Discover()
            print(devices.Value)
            if devices.Value != []:
                for device in devices.Value:
                    with LogixDriver(device.IPAddress) as controller:
                        tags = plc.get_tag_list('*')
                        deviceProperties = comm.GetDeviceProperties()
                        for t in tags.Value:
                            #print(t)
                            if t['tag_type'] == 'atomic':
                                #print(t.DataType)
                                abProvider = ABnode(provider, t['tag_name'], controller, t['data_type'], deviceProperties.Value.ProductName)
                                abProvider.register_node()
                                abProviderList.append(abProvider)
            else:
                with LogixDriver(device.IPAddress) as controller:   
                    tags = plc.get_tag_list('*')
                        deviceProperties = comm.GetDeviceProperties()
                        for t in tags.Value:
                            print(t)
                            if t['tag_type'] == 'atomic':
                                #print(t.DataType)
                                abProvider = ABnode(provider, t['tag_name'], controller, t['data_type'], deviceProperties.Value.ProductName)
                                abProvider.register_node()
                                abProviderList.append(abProvider)

               


            print("INFO Running endless loop...", flush=True)
            while provider.is_connected():
                time.sleep(1.0)  # Seconds

            print("ERROR Data Layer Provider is disconnected", flush=True)

            for i in abProviderList:
                i.unregister_node()
                del i

            print("Stopping Data Layer provider:", end=" ", flush=True)
            result = provider.stop()
            print(result, flush=True)

        # Attention: Doesn't return if any provider or client instance is still running
        stop_ok = datalayer_system.stop(False)
        print("System Stop", stop_ok, flush=True)

if __name__ == '__main__':
    main()
