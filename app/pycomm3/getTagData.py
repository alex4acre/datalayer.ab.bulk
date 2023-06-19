from pycomm3 import LogixDriver

def structSorter(structItems):
    
    abList = []
    for key in structItems.keys():
        if 'array' in structItems[key]:
            if structItems[key]['tag_type'] == "atomic" and structItems[key]['array'] == 0:
                path = key 
                tagName = key
                dataType = structItems[key]['data_type']
                abTagTuple = (path, tagName, dataType)
                abList.append(abTagTuple)    
            elif structItems[key]['tag_type'] == 'atomic' and structItems[key]['array'] != 0:
                dataType = structItems[key]['data_type']
                for x in range(structItems[key]['array']):
                    
                    path = key + "/" + str(x)
                    tagName = key + "[" + str(x) + "]"
                    abTagTuple = (path, tagName, dataType)
                    abList.append(abTagTuple)
            elif structItems[key]['tag_type'] == "struct":
                name = structItems[key]['data_type']['name']
                sortedStruct = structSorter(structItems[key]["data_type"]["internal_tags"])
                for i in sortedStruct:
                    updatedPath = (name + "/" + i[0], name + "." + i[1], i[2]) 
                    abList.append(updatedPath)       
        elif structItems[key]['tag_type'] == "atomic":
            path = key
            tagName = key
            dataType = structItems[key]['data_type']
            abTagTuple = (path, tagName, dataType)
            abList.append(abTagTuple)
    return abList 

def tagSorter(tag):
    abList = []
    if tag['tag_type'] == 'atomic' and tag['dim'] == 0:
        path = tag["data_type"]  + "/" + tag["tag_name"]
        abTagTuple = (path, tag['tag_name'], tag['data_type'])
        abList.append(abTagTuple)
    elif tag['tag_type'] == 'atomic' and tag['dim'] != 0:
        for x in range(tag["dimensions"][0]):
            path = tag["data_type"]  + "/" + tag["tag_name"] + "/" + str(x)
            abTagTuple = (path, tag['tag_name'] + "[" + str(x) + "]", tag['data_type'])
            abList.append(abTagTuple)
    elif tag['tag_type'] != 'atomic':
        abStructList = []
        tagName =  tag['tag_name']
        newList = structSorter(tag["data_type"]["internal_tags"])
        for i in newList:
            updatedPath = ("STRUCT/" + tagName + "/" + i[0], tagName + "." + i[1], i[2]) 
            abList.append(updatedPath)
    return abList 

with LogixDriver('192.168.1.90') as plc:
    tag_List = plc.get_tag_list("*")
    structItems = plc.tags["TestStruct"]
    #print(tag_List)
    print(structItems)
    #print("\n")
    #print(structItems["data_type"]["internal_tags"])
    #print("\n")
    #holdData = structItems["data_type"]["internal_tags"]
    #for key in holdData.keys():
    #    print("\n")
    #    print(key)
    #    print (structItems["data_type"]["internal_tags"][key])
    for t in tag_List:
        sortedTags = tagSorter(t)
        for i in sortedTags:
            print(i)