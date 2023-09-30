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

from app.ab_provider_node import ABnode
                    
def structSorter(structItems):
    abList = []
    for key in structItems.keys():
        if 'array' in structItems[key]:
            if structItems[key]['tag_type'] == "atomic" and structItems[key]['array'] == 0:
                path = key 
                tagName = key
                dataType = structItems[key]['data_type']
                #abTagTuple = (dataType + "/" + path, tagName, dataType)
                abTagTuple = (path, tagName, dataType)
                abList.append(abTagTuple)    
            elif structItems[key]['tag_type'] == 'atomic' and structItems[key]['array'] != 0:
                dataType = structItems[key]['data_type']
                for x in range(structItems[key]['array']):
                    
                    path = key + "/" + str(x)
                    tagName = key + "[" + str(x) + "]"
                    #abTagTuple = ("ARRAY/" + path, tagName, dataType)
                    abTagTuple = (path, tagName, dataType)
                    abList.append(abTagTuple)
            elif structItems[key]['tag_type'] == "struct":
                name = structItems[key]['data_type']['name']
                sortedStruct = structSorter(structItems[key]["data_type"]["internal_tags"])
                for i in sortedStruct:
                    #updatedPath = ("STRUCT" + "/" + name + "/" + i[0], key + "." + i[1], i[2]) 
                    updatedPath = (name + "/" + i[0], key + "." + i[1], i[2]) 
                    abList.append(updatedPath)       
        elif structItems[key]['tag_type'] == "atomic":
            path = key
            tagName = key
            dataType = structItems[key]['data_type']
            #abTagTuple = (dataType + "/" + path, tagName, dataType)
            abTagTuple = (path, tagName, dataType)
            abList.append(abTagTuple)
    return abList 

def tagSorter(tag):
    abList = []
    if tag['tag_type'] == 'atomic' and tag['dim'] == 0:
        #path = tag["data_type"]  + "/" + tag["tag_name"]
        path = tag["tag_name"]
        abTagTuple = (path, tag['tag_name'], tag['data_type'])
        abList.append(abTagTuple)
    elif tag['tag_type'] == 'atomic' and tag['dim'] != 0:
        for x in range(tag["dimensions"][0]):
            #path = tag["data_type"]  + "/" + tag["tag_name"] + "/" + str(x)
            path = tag["tag_name"] + "/" + str(x)
            abTagTuple = (path, tag['tag_name'] + "[" + str(x) + "]", tag['data_type'])
            abList.append(abTagTuple)
    elif tag['tag_type'] != 'atomic':
        abStructList = []
        tagName = tag['tag_name']
        newList = structSorter(tag["data_type"]["internal_tags"])
        for i in newList:
            #updatedPath = ("STRUCT/" + tagName + "/" + i[0], tagName + "." + i[1], i[2]) 
            updatedPath = (tagName + "/" + i[0], tagName + "." + i[1], i[2]) 
            abList.append(updatedPath)
    return abList      

def addData(tag, provider, connection, controller):
    tagDict = {}
    corePath = tag[0]
    if corePath.find("Program:") != -1:
        corePath = corePath.replace("Program:", "")
        pathSplit = corePath.split(".")
        abProvider = ABnode(provider, tag[1], connection, tag[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + connection.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
    else:
        abProvider = ABnode(provider, tag[1], connection, tag[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + connection.IPAddress + "/" + "ControllerTags" + "/" + tag[0], tagDict)    
    abProvider.register_node()
    return abProvider

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
            #print(snap_path)

            #get the path to the config data for the application 
            config = "/var/snap/rexroth-solutions/common/solutions/activeConfiguration/AllenBradley/config.json"
            print(config)
            with open(config) as jsonConfig:
                configdata = json.load(jsonConfig)
                print(configdata) 
                
            abProviderList = []
            abTagList = []
            #comm = PLC()
            tagDict = {}
            with PLC() as comm:
                devices = comm.Discover()
                for device in devices.Value:
                    print('Found Device: ' + device.IPAddress + '  Product Code: ' + device.ProductName + " " + str(device.ProductCode) + '  Vendor/Device ID:' + device.Vendor + " " + str(device.DeviceID) + '  Revision/Serial:' + device.Revision + " " + device.SerialNumber)
            if snap_path is not None: 
                #start the process of checking for the variables
                print("autoscan = " + configdata['scan'])        
                if configdata['scan'] != "true":
                    applications = configdata['controllers']
                    print(applications)
                    for application in applications:
                        comm = PLC()
                        comm.IPAddress = application["ip"]
                        print("Adding controller at " + application["ip"])
                        with LogixDriver(device.IPAddress) as controller:
                        #    tags = controller.get_tag_list('*')
                        #    for tags in programs["tags"]:
                        #        print(t)
                        #        sortedTags = tagSorter(t)        
                        #        for i in sortedTags:
                        #            corePath = i[0]
                        #            if corePath.find("Program:") != -1:
                        #                corePath = corePath.replace("Program:", "")
                        #                pathSplit = corePath.split(".")
                        #                abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
                        #            else:
                        #                abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + "ControllerTags" + "/" + i[0], tagDict)    
                        #            abProvider.register_node()
                        #            abProviderList.append(abProvider)
                            for programs in application["programs"]:
                                print(programs.keys())
                                for program in programs.keys():
                                    for tag in programs[program]["tags"]:
                                        if program != "controller": 
                                            t = "Program:" + program + "." + tag
                                        else:
                                            t = tag
                                        print(t)
                                        sortedTags = tagSorter(controller.get_tag_info(t))        
                                        for i in sortedTags:
                                            abProviderList.append(addData(i, provider, comm, controller))
                                            #corePath = i[0]
                                            #if corePath.find("Program:") != -1:
                                            #    corePath = corePath.replace("Program:", "")
                                            #    pathSplit = corePath.split(".")
                                            #    abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
                                            #else:
                                            #    abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + "ControllerTags" + "/" + i[0], tagDict)    
                                            #abProvider.register_node()
                                            #abProviderList.append(abProvider)
                elif devices.Value != []:
                    print("adding auto-scanned devices")
                    for device in devices.Value:
                        comm = PLC()
                        comm.IPAddress = device.IPAddress
                        with LogixDriver(device.IPAddress) as controller:
                            tags = controller.get_tag_list('*')
                            for t in tags:
                                sortedTags = tagSorter(t)        
                                for i in sortedTags:
                                    corePath = i[0]
                                    if corePath.find("Program:") != -1:
                                        corePath = corePath.replace("Program:", "")
                                        pathSplit = corePath.split(".")
                                        abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
                                    else:
                                        abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + "ControllerTags" + "/" + i[0], tagDict)    
                                    abProvider.register_node()
                                    abProviderList.append(abProvider)
                else:
                    print('No devices found on startup')  
            else:
                comm = PLC()
                comm.IPAddress = "192.168.1.90"
                with LogixDriver("192.168.1.90") as controller:
                    tags = controller.get_tag_list('*')
                    print(controller.info)
                    for t in tags:
                        sortedTags = tagSorter(t)        
                        for i in sortedTags:
                            corePath = i[0]
                            if corePath.find("Program:") != -1:
                                corePath = corePath.replace("Program:", "")
                                pathSplit = corePath.split(".")
                                abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
                            else:
                                abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + "ControllerTags" + "/" + i[0], tagDict)    
                            abProvider.register_node()
                            abProviderList.append(abProvider)
                    
            print("INFO Running endless loop...", flush=True)
            while provider.is_connected():
                time.sleep(1.0)  # Seconds


            print("ERROR Data Layer Provider is disconnected", flush=True)

            for i in abProviderList:
                i.unregister_node()
                del i

            comm.Close()
            controller.close(0)

            print("Stopping Data Layer provider:", end=" ", flush=True)
            result = provider.stop()
            print(result, flush=True)

        # Attention: Doesn't return if any provider or client instance is still running
        stop_ok = datalayer_system.stop(False)
        print("System Stop", stop_ok, flush=True)

if __name__ == '__main__':
    main()
