from pylogix import PLC

with PLC() as comm:
    comm.IPAddress = '192.168.1.70'
    tags = comm.GetTagList()
    print(tags)
    for t in tags.Value:
        print(t.TagName, t.DataType)
        ret = comm.Read(t.TagName)
        print(t.DataTypeValue)
        #print(ret.Value)
    comm.Close()