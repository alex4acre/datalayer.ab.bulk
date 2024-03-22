
            # Path to compiled files
            snap_path = os.getenv('SNAP')
            if snap_path is None:
                config = "./dEV/config.json"
            else:
                config = "/var/snap/rexroth-solutions/common/solutions/activeConfiguration/AllenBradley/config.json"
            
            #Get the time the files was modified
            fileTime =  os.stat(config).st_mtime
            print(fileTime)
            print(config)
            with open(config) as jsonConfig:
                configdata = json.load(jsonConfig)
                print(configdata) 
            
            abProviderList = []
            abTagList = []
            #comm = PLC()
            tagDict = {}
            with PLC() as comm:
                devices = comm.Discover()
                for device in devices.Value:
                    print('Found Device: ' + device.IPAddress + '  Product Code: ' + device.ProductName + " " + str(device.ProductCode) + '  Vendor/Device ID:' + device.Vendor + " " + str(device.DeviceID) + '  Revision/Serial:' + device.Revision + " " + device.SerialNumber)
            if snap_path is not None: 
                #start the process of checking for the variables
                print("autoscan = " + configdata['scan'])        
                if configdata['scan'] != "true":
                    applications = configdata['controllers']
                    print(applications)
                    for application in applications:
                        comm = PLC()
                        comm.IPAddress = application["ip"]
                        print("Adding controller at " + application["ip"])
                        with LogixDriver(device.IPAddress) as controller:
                            if "programs" in application:
                                for programs in application["programs"]:
                                    print(programs.keys())
                                    for program in programs.keys():
                                        if "tags" in programs[program]:
                                            for tag in programs[program]["tags"]:
                                                if program != "controller": 
                                                    t = "Program:" + program + "." + tag
                                                else:
                                                    t = tag
                                                print(t)
                                                sortedTags = tagSorter(controller.get_tag_info(t))        
                                                for i in sortedTags:
                                                    abProviderList.append(addData(i, provider, comm, controller))
                                        else:       
                                            if program != "controller": 
                                                t = "Program:" + program
                                            else:
                                                t = ""
                                            tags = controller.get_tag_list(t) 
                                            for t in tags:
                                                if t['tag_name'].find("Program:.") != -1:
                                                    t['tag_name'] = t['tag_name'].split(".")[1]
                                                sortedTags = tagSorter(t)        
                                                for i in sortedTags:
                                                    corePath = i[0]
                                                    if corePath.find("Program:") != -1:
                                                        corePath = corePath.replace("Program:", "")
                                                        pathSplit = corePath.split(".")
                                                        abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
                                                    else:
                                                        abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + "ControllerTags" + "/" + i[0], tagDict)    
                                                    abProvider.register_node()
                                                    abProviderList.append(abProvider)    
                            else:
                                tags = controller.get_tag_list('*')
                                for t in tags:
                                    sortedTags = tagSorter(t)        
                                    for i in sortedTags:
                                        corePath = i[0]
                                        if corePath.find("Program:") != -1:
                                            corePath = corePath.replace("Program:", "")
                                            pathSplit = corePath.split(".")
                                            abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
                                        else:
                                            abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + "ControllerTags" + "/" + i[0], tagDict)    
                                        abProvider.register_node()
                                        abProviderList.append(abProvider)                    
                elif devices.Value != []:
                    print("adding auto-scanned devices")
                    for device in devices.Value:
                        comm = PLC()
                        comm.IPAddress = device.IPAddress
                        with LogixDriver(device.IPAddress) as controller:
                            tags = controller.get_tag_list('*')
                            for t in tags:
                                sortedTags = tagSorter(t)        
                                for i in sortedTags:
                                    corePath = i[0]
                                    if corePath.find("Program:") != -1:
                                        corePath = corePath.replace("Program:", "")
                                        pathSplit = corePath.split(".")
                                        abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
                                    else:
                                        abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--").replace(" ","_") + "/" + comm.IPAddress + "/" + "ControllerTags" + "/" + i[0], tagDict)    
                                    abProvider.register_node()
                                    abProviderList.append(abProvider)
                else:
                    print('No devices found on startup')  
            else:
                comm = PLC()
                comm.IPAddress = "192.168.1.90"
                with LogixDriver("192.168.1.90") as controller:
                    tags = controller.get_tag_list('*')
                    print(controller.info)
                    for t in tags:
                        sortedTags = tagSorter(t)        
                        for i in sortedTags:
                            corePath = i[0]
                            if corePath.find("Program:") != -1:
                                corePath = corePath.replace("Program:", "")
                                pathSplit = corePath.split(".")
                                abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + pathSplit[0] + "/" + pathSplit[1], tagDict)
                            else:
                                abProvider = ABnode(provider, i[1], comm, i[2], controller.info["product_name"].replace("/", "--") + "/" + comm.IPAddress + "/" + "ControllerTags" + "/" + i[0], tagDict)    
                            abProvider.register_node()
                            abProviderList.append(abProvider)