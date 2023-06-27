from pylogix import PLC

with PLC() as comm:
    comm.IPAddress = '192.168.1.90'
    tags = comm.GetTagList("")
    programs = comm.GetProgramsList()
    print(programs)
    for i in tags.Value:
        print(i)
    #for t in tags.Value:
    #    print(t.TagName)
    #    print(t)
    ##    ret = comm.Read(t.TagName)
     #   print(t.DataTypeValue)
        #print(ret.Value)
    comm.Close()