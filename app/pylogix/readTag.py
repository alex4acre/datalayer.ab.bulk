from pylogix import PLC
from struct import pack, unpack_from, pack_into

comm = PLC()
comm.IPAddress = '192.168.1.90'
#comm.tag
ret = (comm.Read('Program:MainProgram.Vars_Out[0]'))
print(ret.Value)
#(comm.Write('Program:MainProgram.Vars.Index_2', 25.0))
#data = unpack_from('<f', ret.Value, 4)
#print(data)
#print(ret.Value)
#buffer = bytearray(ret.Value)
#write_Data = pack_into('<f', buffer, 4, 10.0)
#print(list(buffer))

#comm.Write(ret[0], ret[1])
#print(data)
#print(list(bytes(ret)))
comm.Close()