from pylogix import PLC

comm = PLC()
comm.IPAddress = '192.168.1.70'

ret = comm.Read('Program:MainProgram.Accel')
print(ret)
comm.Close()