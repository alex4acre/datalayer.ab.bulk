from pylogix import PLC

with PLC() as comm:
    devices = comm.Discover()
    print(devices)
    for device in devices.Value:
        print(device.IPAddress)
        print('  Product Code: ' + device.ProductName + " " + str(device.ProductCode))
        print('  Vendor/Device ID:' + device.Vendor + " " + str(device.DeviceID))
        print('  Revision/Serial:' + device.Revision + " " + device.SerialNumber)
        print('')