if devices.Value != []:
                for device in devices.Value:
                    comm.IPAddress = device.IPAddress
                    tags = comm.GetTagList()
                    deviceProperties = comm.GetDeviceProperties()
                    print(deviceProperties.Value.ProductName)
                    for t in tags.Value:
                        #print(t)
                        if t.Array == 0 and t.Struct == 0 and (t.DataType != ""):
                            #print(t.DataType)
                            abProvider = ABnode(provider, t.TagName, comm, t.DataType, t.DataTypeValue, deviceProperties.Value.ProductName)
                            abProvider.register_node()
                            abProviderList.append(abProvider)
            else:
                comm.IPAddress = '192.168.1.70'    
                tags = comm.GetTagList()
                deviceProperties = comm.GetDeviceProperties()
                print(deviceProperties.Value.ProductName)
                for t in tags.Value:
                    #print(t)
                    if t.Array == 0 and t.Struct == 0 and (t.DataType != ""):
                        abProvider = ABnode(provider, t.TagName, comm, t.DataType, t.DataTypeValue, deviceProperties.Value.ProductName)
                        abProvider.register_node()
                        abProviderList.append(abProvider) 