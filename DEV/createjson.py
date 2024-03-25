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
import pprint

import pycomm3
from pycomm3 import LogixDriver

#from helper.ctrlx_datalayer_helper import get_provider

#from app.ab_provider_node import ABnode
                    
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
    config = "dEV/config.json"
    print(config)
    with open(config) as jsonConfig:
        configdata = json.load(jsonConfig)
        print(configdata) 
        applications = configdata['controllers']
        print(applications)
       # for application in applications:
        with PLC() as comm:
            #devices = comm.Discover()
            #print(devices)
            #for device in devices.Value:
                #print(device)
                #print('Found Device: ' + device.IPAddress + '  Product Code: ' + device.ProductName + " " + str(device.ProductCode) + '  Vendor/Device ID:' + device.Vendor + " " + str(device.DeviceID) + '  Revision/Serial:' + device.Revision + " " + device.SerialNumber)
            comm = PLC()
            comm.IPAddress = "192.168.1.90"
            with LogixDriver("192.168.1.90") as controller:
                print(controller.get_plc_info())
                tags = controller.get_tag_list('*')
                for t in tags:
                    print(t)
                for program in programs.keys():
                    print(program)
                    print(programs[program])
                    tags = programs[program]["tags"]
                    for tag in programs[program]["tags"]:
                        print(tag)
                        if program != "controller": 
                            t = "Program:" + program + "." + tag
                        else:
                            t = tag
                        print(controller.get_tag_info(t))
                #print(program)
                #for tag in program["tags"]:
                #    t = program + "." + tag
                #    print(t)
            tags = controller.get_tag_list('*')
            #for t in tags:
            #    pprint.pprint(t)


if __name__ == '__main__':
    main()
