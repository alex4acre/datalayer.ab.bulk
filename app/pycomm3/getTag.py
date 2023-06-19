from pycomm3 import LogixDriver

with LogixDriver('192.168.1.90') as plc:
    data = plc.read("TestStruct.struct.rTest")
    print(data)

    #for key in index:  
    #    data[key] = 5
    #plc.write("Program:MainProgram.Vars", data)
    #print(data)

    #print(plc.write("Program:MainProgram.Vars_Out[23]", [5.0]))
    #print(plc.read("Program:MainProgram.Vars_In[23]{1}"))