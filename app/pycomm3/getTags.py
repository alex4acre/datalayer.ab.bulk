from pycomm3 import LogixDriver

with LogixDriver('192.168.1.90') as plc:
    tag_List = plc.get_tag_list(program="MainProgram")
    #print(plc.tags.keys())
    #print(plc.info)
    for t in tag_List:
        print(t["tag_name"])
        #if t["tag_type"] == "struct": 
        #    print(t["tag_type"])
    #    name = t["tag_name"].split(".")
    #    for n in name:  
    #        print(n) 
        #application = name[1].split(".")
        #for a in application:
        #    print(a)
        #value = (plc.read(t["tag_name"]))
        #print(value[1])
        #print(plc.read(t["tag_name"]))
        #if t["dim"] != 0: 
        #    print(t["dimensions"][0])

def find_attributes():
    with LogixDriver('192.168.1.90') as plc:
        ...  # do nothing, we're just letting the plc initialize the tag list
        tag_List = plc.get_tag_list()
        print(tag_List)

