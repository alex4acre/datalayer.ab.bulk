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
from app.ab_provider_node_bulk import ABnode_Array

def sortTags(tag, tagPreamble : str):
    abTagList = []
    if 'array' not in tag:
        if tag['tag_type'] == 'atomic' and tag['dim'] == 0:
            path = tagPreamble + tag["data_type"]  + "/" + tag["tag_name"]
            return (tag['tag_name'], tag['data_type'], path)
        elif tag['tag_type'] == 'atomic' and tag['dim'] != 0:
            length = tag["dimensions"][0]
            for x in range(tag["dimensions"][0]):
                path = tagPreamble + "ARRAY/" + tag["data_type"]  + "/" + tag["tag_name"] + "/" + str(x)
                abTagList.append((tag['tag_name'] + "[" + str(x) + "]", tag['data_type'], path))
            return abTagList
        elif tag['tag_type'] != 'atomic':
            #structItems = tag['tag_name']
            print(tag)
            for key in tag["data_type"]["internal_tags"].keys():
                print(key)
                print (tag["data_type"]["internal_tags"][key])
                if 'array' in tag["data_type"]["internal_tags"][key]:
                    if tag["data_type"]["internal_tags"][key]['tag_type'] == "atomic" and tag["data_type"]["internal_tags"][key]['array'] == 0:
                        newTagItem = sortTags(tag["data_type"]["internal_tags"][key], tagPreamble + "STRUCT/")
                        if type(newTagItem) is list:
                            abTagList = abTagList + newTagItem
                        else:
                            abTagList.append(newTagItem)
                        return abTagList    
    if 'array' in tag:
        if tag['tag_type'] == 'atomic' and tag['array'] == 0:
            path = tagPreamble + tag["data_type"]  + "/" + tag["tag_name"]
            return (tag['tag_name'], tag['data_type'], path)
        elif tag['tag_type'] == 'atomic' and tag['array'] != 0:
            length = tag["dimensions"][0]
            for x in range(tag["dimensions"][0]):
                path = tagPreamble + "ARRAY/" + tag["data_type"]  + "/" + tag["tag_name"] + "/" + str(x)
                abTagList.append((tag['tag_name'] + "[" + str(x) + "]", tag['data_type'], path))
            return abTagList
        elif tag['tag_type'] != 'atomic':
            #structItems = tag['tag_name']
            #print(structItems)
            for key in tag["data_type"]["internal_tags"].keys():
                #print(key)
                if 'array' in tag["data_type"]["internal_tags"][key]:
                    if tag["data_type"]["internal_tags"][key]['tag_type'] == "atomic" and tag["data_type"]["internal_tags"][key]['array'] == 0:
                        newTagItem = tag(structItems["data_type"]["internal_tags"][key], tagPreamble + "STRUCT/")  
                        if type(newTagItem) is list:
                            abTagList = abTagList + newTagItem
                        else:
                            abTagList.append(newTagItem)
                        return abTagList    
                    
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
            abTagList = []
            comm = PLC()
            devices = comm.Discover()
            print(devices.Value)
            #if devices.Value != []:
            if False:
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
            elif False:
                comm = PLC()
                comm.IPAddress = "192.168.1.90"
                with LogixDriver("192.168.1.90") as controller:
                        tags = controller.get_tag_list('*')
                        deviceProperties = comm.GetDeviceProperties()
                        for t in tags:
                            print(t["tag_name"])
                            if t['tag_type'] == 'atomic' and t['dim'] == 0:
                                path = controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + t["data_type"]  + "/" + t["tag_name"]
                                abTagTuple = (path, t['tag_name'], t['data_type'])
                                abProvider = ABnode(provider, t['tag_name'], comm, t['data_type'], path)
                                abProvider.register_node()
                                abProviderList.append(abProvider)
                            elif t['tag_type'] == 'atomic' and t['dim'] != 0:
                                length = t["dimensions"][0]
                                for x in range(t["dimensions"][0]):
                                    path = controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/ARRAY/" + t["data_type"]  + "/" + t["tag_name"] + "/" + str(x)
                                    
                                    abTagTuple = (path, t['tag_name'] + "[" + str(x) + "]", t['data_type'])
                                    abProvider = ABnode_Array(provider, t['tag_name'] + "[" + str(x) + "]", comm, t['data_type'], path)
                                    abProvider.register_node()
                                    abProviderList.append(abProvider)
                            elif t['tag_type'] != 'atomic':
                                structItems = controller.tags[t['tag_name']]
                                #print(structItems)
                                for key in structItems["data_type"]["internal_tags"].keys():
                                    print(key)
                                    if 'array' in structItems["data_type"]["internal_tags"][key]:
                                        if structItems["data_type"]["internal_tags"][key]['tag_type'] == "atomic" and structItems["data_type"]["internal_tags"][key]['array'] == 0:
                                            path = controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/STRUCT/" + t["tag_name"] + "/" + key
                                            tagName = t['tag_name'] + "." + key
                                            dataType = structItems["data_type"]["internal_tags"][key]['data_type']
                                            abProvider = ABnode(provider, tagName, comm, dataType, path)
                                            abProvider.register_node()
                                            abProviderList.append(abProvider)
                                    elif structItems["data_type"]["internal_tags"][key]['tag_type'] == "atomic":
                                        path = controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/STRUCT/" + t["tag_name"] + "/" + key
                                        tagName = t['tag_name'] + "." + key
                                        dataType = structItems["data_type"]["internal_tags"][key]['data_type']
                                        abProvider = ABnode(provider, tagName, comm, dataType, path)
                                        abProvider.register_node()
                                        abProviderList.append(abProvider)
            elif False:
                abList_ProviderData = [];
                comm = PLC()
                comm.IPAddress = "192.168.1.90"
                with LogixDriver("192.168.1.90") as controller:
                        tags = controller.get_tag_list('*')
                        deviceProperties = comm.GetDeviceProperties()
                        for t in tags:
                            print(t["tag_name"])
                            tagSetup = sortTags(t, controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/")
                            if tagSetup != None:
                                if type(tagSetup) is list:
                                    abList_ProviderData = abList_ProviderData + tagSetup
                                else:
                                    abList_ProviderData.append(tagSetup)    
                                #for t in tagSetup:
                                 #   abList_ProviderData.append(t)
                            #if t['tag_type'] == 'atomic' and t['dim'] == 0:
                            #    path = controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + t["data_type"]  + "/" + t["tag_name"]
                            #    abTagTuple = (path, t['tag_name'], t['data_type'])
                        for i in abList_ProviderData:
                            print(i)    
                            print("\n")
                        for i in abList_ProviderData:
                            print(i)
                            abProvider = ABnode(provider, i[0], comm, i[1], i[2])
                            abProvider.register_node()
                            abProviderList.append(abProvider)
            elif False:
                comm = PLC()
                comm.IPAddress = "192.168.1.90"
                with LogixDriver("192.168.1.90") as controller:
                        tags = controller.get_tag_list('*')
                        deviceProperties = comm.GetDeviceProperties()                        
                        for t in tags:
                            print(t["tag_name"])
                            sortedTags = tagSorter(t)        
                            for i in sortedTags:
                                abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + i[0])
                                print(i[1])
                                abProvider.register_node()
                                abProviderList.append(abProvider)
            else:
                comm = PLC()
                comm.IPAddress = "192.168.1.90"
                with LogixDriver("192.168.1.90") as controller:
                        programList = comm.GetProgramsList()
                        tags = controller.get_tag_list('*')
                        print(controller.info)
                        for t in tags:
                            #print(t["tag_name"])
                            sortedTags = tagSorter(t)        
                            for i in sortedTags:
                                corePath = i[0]
                                if corePath.find("Program:") != -1:
                                    corePath = corePath.replace("Program:", "")
                                    pathSplit = corePath.split(".")
                                    typeSplit = pathSplit[0].split("/")
                                    #abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + typeSplit[1] + "/" + typeSplit[0] + "/" + pathSplit[1])
                                    abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1])
                                else:
                                    abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + "controller" + "/" + i[0])    
                                #print(i[1])
                                abProvider.register_node()
                                abProviderList.append(abProvider)
                        #for program in programList.Value: 
                        #    programName = program       
                        #    programName.replace("Program:", "")       
                        #    tags = controller.get_tag_list(programName)
                        #    for t in tags:        
                        #        print(t)
                        #        print("\n")
                        #        #print(t["tag_name"])
                        #        sortedTags = tagSorter(t)        
                        #        for i in sortedTags:
                        #            abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + i[0])
                                 #   print(i[1])
                        #            abProvider.register_node()
                        #            abProviderList.append(abProvider)        


                    




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
