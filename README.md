# ctrlX AB Data Layer Provider

The app finds AB controllers on the local network and in the same subnet as the ctrlX and puts all variables onto the datalayer. 

This work is an extension of the [pylogix  project](https://pypi.org/project/pylogix/) and the [pycomm3 project](https://pypi.org/project/pycomm3/).

## Preparation

After installation connect an AB controller to the local network of the core. Restart the core. Verify the data is available on the datalayer of the core. This data is also available on the OPC-UA server of the core if equipped. 

A config.json file is located in the app data of the controller under the AllenBradley folder. This config file can be used to exclusively configure the app to get data from a specific controller, program and set of tags. 

```json
{
  "scan": "true", //true by default, set false to select controllers
  "controllers": [
    {
      "ip": "192.168.1.90", //IP of first control
      "programs": [
        {
          "MainProgram": { //name of program wtih tages
            "tags": [ //name of tags in program
              "Accel",  
              "VariableManager"
            ]
          }
        },
        {
          "controller": { //controller level tags
            "tags": [ //tags at the controller level
              "iCounter",
              "arErrData"
            ]
          }
        }
      ]
    }
  ]
}
```
 
___

## License

MIT License

Copyright (c) 2021-2022 Bosch Rexroth AG

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
