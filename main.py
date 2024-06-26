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
import json
import ctrlxdatalayer
from ctrlxdatalayer.variant import Result
from pylogix import PLC
import logging
import logging.handlers
from pycomm3 import LogixDriver
from helper.ctrlx_datalayer_helper import get_provider
from app.ab_util import myLogger, tagSorter, addData
from collections import OrderedDict
import time
from app.ab_provider_node_bulk import TimeStats

def runApp(provider, tagList:list):
    # Path to compiled files
    snap_path = os.getenv('SNAP')
    if snap_path is None:
        config = "./DEV/config.json"
    else:
        config = "/var/snap/rexroth-solutions/common/solutions/activeConfiguration/AllenBradley/config.json"
    
    #Get the time the files was modified
    fileTime = os.stat(config).st_mtime
    myLogger("Config modified at UNIX TIME " + str(fileTime), logging.INFO)
    with open(config) as jsonConfig:
        configdata = json.load(jsonConfig)
        myLogger("Config data: " + str(configdata), logging.INFO)
        
    #Define the master list of data
    abProviderList = []
    tagData = []
    tagDict = OrderedDict()
    tagDict['firstEntry'] = 0
    index = 0
    #tagList = []
    #print(configdata)
    #if snap_path is not None: #this means the app is deployed on a target
    #start the process of checking for the variables
    myLogger("Autoscan Setting = " + configdata['scan'], logging.INFO, source=__name__)        
    if configdata['scan'] != "true":
        #if the auto scan is not true then load controllers from file
        if "controllers" in configdata:
            applications = configdata['controllers']
            for application in applications:
                #myLogger('Loading configuration for ' + str(application), logging.INFO, source=__name__)
                comm = PLC()
                comm.IPAddress = application["ip"]
                #myLogger("Adding controller at " + application["ip"], logging.INFO, source=__name__)
                try:
                    with LogixDriver(application["ip"]) as controller:
                        if "programs" in application:
                            for programs in application["programs"]:
                                #cycle through the programs in the application
                                for program in programs.keys():
                                    if "tags" in programs[program]:
                                        tags = programs[program]["tags"]
                                        for tag in tags:
                                            #cycle through the tags in the configuration file
                                            if program != "controller": 
                                                tag = "Program:" + program + "." + tag
                                            else:
                                                tag = tag
                                            #print('Adding Tag: ' + tag)
                                            tagInfo = controller.get_tag_info(tag)

                                            sortedTags = tagSorter(controller.get_tag_info(tag))        
                                            for sortedTag in sortedTags:
                                                #print(sortedTag[1])
                                                tagData.append(sortedTag[1])
                                                #print("\n adding tag: " + sortedTag[1])
                                                tagDict[sortedTag[1]] = tagDict[next(reversed(tagDict))] + 1
                                                abProviderList.append(addData(sortedTag, provider, comm, controller, tagList, tagDict, index))
                                                index = index + 1   
                        #print('Tag Data: \n')
                        #print(tagData)                                                                    
                        return abProviderList, comm, controller, tagData, tagDict
                except:
                    myLogger("Controller at " + comm.IPAddress + " could not be loaded.", logging.ERROR, source=__name__) 
                    return None, None, None, None, None
        else:
            #if no devices were configured in the file, return empty and log the exception
            myLogger('No devices configured in the configuration data.', logging.ERROR, source=__name__)
            return None, None, None, None, None  
                  
def main():

    snap_path = os.getenv('SNAP')
    print(snap_path)
    if snap_path is None:
        config = "./DEV/config.json"
        logPath = "./DEV/info.log"
    else:
        myLogger("cltrX File Path: " + str(snap_path), logging.INFO, source=__name__)
        config = "/var/snap/rexroth-solutions/common/solutions/activeConfiguration/AllenBradley/config.json"
        logPath = "/var/snap/rexroth-solutions/common/solutions/activeConfiguration/AllenBradley/info.log"

    #configure the logger for easier analysis
    logging.basicConfig(filename = logPath, filemode = 'w', format='%(asctime)s:%(msecs)d, %(name)s, %(levelname)s, %(message)s', datefmt= '%H:%M:%S', level=logging.DEBUG)  
       
    myLogger('#######################################################################', logging.DEBUG, source=__name__)
    myLogger('#######################################################################', logging.DEBUG, source=__name__)
    myLogger('#######################################################################', logging.DEBUG, source=__name__)
    myLogger('Initializing application', logging.INFO)   

    with ctrlxdatalayer.system.System("") as datalayer_system:
        datalayer_system.start(False)

        # ip="10.0.2.2", ssl_port=8443: ctrlX virtual with port forwarding and default port mapping
        provider, connection_string = get_provider(datalayer_system)
        if provider is None:
            myLogger("Connecting to " + connection_string + " failed.", logging.ERROR, source=__name__)
            sys.exit(1)

        with provider:  # provider.close() is called automatically when leaving with... block

            result = provider.start()
            if result != Result.OK:
                myLogger("ERROR Starting Data Layer Provider failed with:" + str(result), logging.ERROR, source=__name__)
                return

            tagList = []

            #Start the applicaiton             
            abProviderList, comm, controller, tagData, tagDict = runApp(provider, tagList)

            #here, can truncate the tag list for testing
            tagData = tagData[:]
            #print(tagData)
    
            #comm = PLC()
            #IP Address hard coded for this rough testing...
            #comm.IPAddress = '192.168.1.90'

            #this step is neccessary to copy of the content of the tag data to the new tags, unclear why this is required. 
            tempTagList = comm.Read(tagData)
            for tags in tempTagList:
                tagList.append(tags)

            print("number of items: " + str(len(tagData)))

            loopIndex = 0
            bulkMinTimeToRead = 1000000000
            bulkMaxTimeToRead = 0
            bulkTotalTime = 0
            totalTime = 0
            minCycleTime = 1000000000
            maxCycleTime = 0

            bulkexecutionTime = [1000000000, 0, 0, 0]    
            bulkminTimeData = TimeStats(provider, 'BulkRead/min', 0, bulkexecutionTime, "min cycle time(ms) for bulkread") 
            bulkminTimeData.register_node()
            bulkmaxTimeData = TimeStats(provider, 'BulkRead/max', 1, bulkexecutionTime, "max cycle time(ms) for bulkread")  
            bulkmaxTimeData.register_node()
            bulkavgTimeData = TimeStats(provider, 'BulkRead/avg', 2, bulkexecutionTime, "average cycle time(ms) for bulkread")  
            bulkavgTimeData.register_node()
            


            executionTime = [1000000000, 0, 0, 0]    
            minTimeData = TimeStats(provider, 'CycleTime/min', 0, executionTime, "min cycle time(ms) for complete cycle") 
            minTimeData.register_node()
            maxTimeData = TimeStats(provider, 'CycleTime/max', 1, executionTime, "max cycle time(ms) for complete cycle")  
            maxTimeData.register_node()
            avgTimeData = TimeStats(provider, 'CycleTime/avg', 2, executionTime, "average cycle time(ms) for complete cycle")  
            avgTimeData.register_node()
            loopCounter = TimeStats(provider, 'loops', 3, executionTime, "loops") 
            loopCounter.register_node()
            
            #Get the time the files was modified
            fileTime =  os.stat(config).st_mtime

            #read the list one time to make it faster when reading the second time
            tempTagList = comm.Read(tagData)


            if abProviderList is not None and comm is not None and controller is not None:       
                myLogger('INFO Running endless loop...', logging.INFO, source=__name__)
                startClock = time.time()
                while provider.is_connected():
                    cycleTime = time.time() - startClock
                    startClock = time.time()
                    tic = time.time()
                    tempTagList = comm.Read(tagData)
                    toc = time.time()
                    bulkTimeToRead  = toc - tic
                    bulkMinTimeToRead = min(bulkTimeToRead, bulkMinTimeToRead)
                    bulkMaxTimeToRead = max(bulkTimeToRead, bulkMaxTimeToRead)
                    if loopIndex > 0:
                        minCycleTime = min(cycleTime, minCycleTime)
                        maxCycleTime = max(cycleTime, maxCycleTime)
                        totalTime = totalTime + cycleTime
                        averageCycleTime = totalTime / loopIndex
                        executionTime[0] = minCycleTime * 1000
                        executionTime[1] = maxCycleTime * 1000
                        executionTime[2] = averageCycleTime * 1000

                    #print("time to read: " + str(timeToRead))
                    #print("min time to read: " + str(minTimeToRead))
                    #print("max time to read: " + str(maxTimeToRead))
                    tagIndex = 0
                    #for some reason it is required to copy the tags over to the list that is passed to the function that then does the read/write operation 
                    #perhaps come kind of callback could be used to get this data instead so that upon request the data is directly accessed
                    tic = time.time()
                    for tag in tempTagList:
                        tagList[tagIndex] = tag
                        tagIndex = tagIndex + 1 
                    toc = time.time()  
                    #print("Copy Time: " + str(toc - tic))  
                    #Count the number of loops    
                    loopIndex = loopIndex + 1
                    bulkTotalTime = bulkTotalTime + bulkTimeToRead
                    bulkAverageTimeToRead = totalTime / loopIndex

                    

                    bulkexecutionTime[0] = bulkMinTimeToRead * 1000
                    bulkexecutionTime[1] = bulkMaxTimeToRead * 1000
                    bulkexecutionTime[2] = bulkAverageTimeToRead * 1000
                    executionTime[3] = loopIndex
                    #print("Average time to read: " + str(averageTimeToRead))
                    #print(loopIndex)
                    #time.sleep(1.0)   
                
                    #if (fileTime == os.stat(config).st_mtime):
                    #    time.sleep(1.0)  # Seconds
                    #else:
                    #    fileTime == os.stat(config).st_mtime
                    #    myLogger('"ERROR Data Layer Provider is disconnected', logging.ERROR, source=__name__)
                    #    for node in abProviderList:
                    #        node.unregister_node()
                    #        del node
                    #    comm.Close()
                    #    controller.close(0)
                    #    abProviderList, comm, controller = runApp(provider)
            else: 
                myLogger("Improperly configured application, see application log.", logging.ERROR, source=__name__)            

            myLogger('min time(ms) to read tags: ' + str(1000 * bulkMinTimeToRead), logging.INFO, source=__name__)    
            myLogger('max time(ms) to read tags: ' + str(1000 * bulkMaxTimeToRead), logging.INFO, source=__name__)    
            myLogger('average time(ms) to read tags: ' + str(1000 * bulkAverageTimeToRead), logging.INFO, source=__name__)    
            myLogger('Stopping Data Layer provider', logging.INFO, source=__name__)
            result = provider.stop()
            myLogger('Data Layer Stopped with result: ' + str(result), logging.INFO, source=__name__)

        # Attention: Doesn't return if any provider or client instance is still running
        stop_ok = datalayer_system.stop(False)
        myLogger('System Stop: ' + str(stop_ok), logging.INFO, source=__name__)


if __name__ == '__main__':
    main()
