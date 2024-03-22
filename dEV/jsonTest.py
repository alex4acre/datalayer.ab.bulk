import os
import sys
import time
import json
import pycomm3
from pycomm3 import LogixDriver

                    
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
            

with LogixDriver("192.168.2.90") as controller:
    tags = controller.get_tag_list("MainProgram")
    for tag in tags: 
        for t in tags:
            if t['tag_name'].find("Program:.") != -1:
               t['tag_name'] = t['tag_name'].split(".")[1]
            #print(t)
            sortedTags = tagSorter(t)        
            for i in sortedTags:
                print(i)
        