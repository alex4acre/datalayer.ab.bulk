from pylogix import PLC

with PLC() as comm:
    comm.IPAddress = '192.168.1.70'
    prop = comm.GetModuleProperties(0)
    print(prop.Value.ProductName, prop.Value.Revision)