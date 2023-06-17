from pycomm3 import LogixDriver

with LogixDriver('192.168.1.90') as plc:
    tag_List = plc.get_tag_list("*")
    structItems =plc.tags["Program:MainProgram.XPos"]
    print(structItems)
    #for key in structItems["data_type"]["internal_tags"].keys():
    #    print (structItems["data_type"]["internal_tags"][key])
    #print(structItems["data_type"]["internal_tags"].keys())