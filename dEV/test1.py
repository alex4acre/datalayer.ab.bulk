import json
configdata = json.loads('{    "scan": "true",    "controllers": [      {        "ip": "192.168.1.90",        "programs": [          {            "MainProgram": {              "tags": ""            }          },          {            "controller": {              "tags": [                "iCounter",                "arErrData"              ]            }          }        ]      }    ]  }')
applications = configdata['controllers']
for application in applications:
    for programs in application["programs"]:
        for program in programs.keys():
            #print(program)
            #print(programs[program]["tags"])
            for tag in programs[program]["tags"]: 
                print(tag)
                