# LTRCOL-2574 Sample Portal

This Repo contains a sample web portal (Provisioning Portal) that allows you to perform certain administrative and/or user functions on Cisco Collaboration products. This Repo is accompanying CiscoLive Lab LTRCOL-2574

* master Branch contains the fully built-out Portal
* skeleton Branch contains a partially built-out Portal that is meant to be used while Following the [CiscoLive Lab Guide](https://collabapilab.ciscolive.com/)


## Steps to start up the Portal after Cloning

### Step 1

Make sure python3 is installed (```/usr/bin/env python3 --version```).  You may also install/use a virtual environment.  

### Step 2

Install all python requirements with:

```pip install -r requirements.txt```

### Step 3

Now you need to start the web service with ```./app.py``` in order to start the Flask development server.

### Step 4

The web server is ready once these messages appear:

```
 * Serving Flask app "flaskr" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 255-014-512
 ```

### Step 5

In your browser, access the page using `http://localhost:5000`

## VS Code Debug Run Setup ##

In your VSCode go to your Command Palette (Ctrl + Shift + P /  Cmd + Shift + P) and Type Debug: Open launch.json

Populate your your launch.json file with the following or append to your existing configurations list:

```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Start LTRCOL-2574 Portal",
            "type": "python",
            "request": "launch",
            "module": "flask",
            // https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "0"
            },
            "args": [
                "run",
                "--host=127.0.0.1",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true
        },  
    ]
}
```

## Sample Code License

These terms govern this Cisco Systems, Inc. (“Cisco”), example or demo source code and its associated documentation (together, the “Sample Code”). By downloading, copying, modifying, compiling, or redistributing the Sample Code, you accept and agree to be bound by the following terms and conditions (the “License”). If you are accepting the License on behalf of an entity, you represent that you have the authority to do so (either you or the entity, “you”). Sample Code is not supported by Cisco TAC and is not tested for quality or performance. This is your only license to the Sample Code and all rights not expressly granted are reserved.

1. LICENSE GRANT: Subject to the terms and conditions of this License, Cisco hereby grants to you a perpetual, worldwide, non-exclusive, non-transferable, non-sublicensable, royalty-free license to copy and modify the Sample Code in source code form, and compile and redistribute the Sample Code in binary/object code or other executable forms, in whole or in part, solely for use with Cisco products and services. For interpreted languages like Java and Python, the executable form of the software may include source code and compilation is not required.

2. CONDITIONS: You shall not use the Sample Code independent of, or to replicate or compete with, a Cisco product or service. Cisco products and services are licensed under their own separate terms and you shall not use the Sample Code in any way that violates or is inconsistent with those terms (for more information, please visit: www.cisco.com/go/terms ).

3. OWNERSHIP: Cisco retains sole and exclusive ownership of the Sample Code, including all intellectual property rights therein, except with respect to any third-party material that may be used in or by the Sample Code. Any such third-party material is licensed under its own separate terms (such as an open source license) and all use must be in full accordance with the applicable license. This License does not grant you permission to use any trade names, trademarks, service marks, or product names of Cisco. If you provide any feedback to Cisco regarding the Sample Code, you agree that Cisco, its partners, and its customers shall be free to use and incorporate such feedback into the Sample Code, and Cisco products and services, for any purpose, and without restriction, payment, or additional consideration of any kind. If you initiate or participate in any litigation against Cisco, its partners, or its customers (including cross-claims and counter-claims) alleging that the Sample Code and/or its use infringe any patent, copyright, or other intellectual property right, then all rights granted to you under this License shall terminate immediately without notice.

4. LIMITATION OF LIABILITY: CISCO SHALL HAVE NO LIABILITY IN CONNECTION WITH OR RELATING TO THIS LICENSE OR USE OF THE SAMPLE CODE, FOR DAMAGES OF ANY KIND, INCLUDING BUT NOT LIMITED TO DIRECT, INCIDENTAL, AND CONSEQUENTIAL DAMAGES, OR FOR ANY LOSS OF USE, DATA, INFORMATION, PROFITS, BUSINESS, OR GOODWILL, HOWEVER CAUSED, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

5. DISCLAIMER OF WARRANTY: SAMPLE CODE IS INTENDED FOR EXAMPLE PURPOSES ONLY AND IS PROVIDED BY CISCO “AS IS” WITH ALL FAULTS AND WITHOUT WARRANTY OR SUPPORT OF ANY KIND. TO THE MAXIMUM EXTENT PERMITTED BY LAW, ALL EXPRESS AND IMPLIED CONDITIONS, REPRESENTATIONS, AND WARRANTIES INCLUDING, WITHOUT LIMITATION, ANY IMPLIED WARRANTY OR CONDITION OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, SATISFACTORY QUALITY, NON-INTERFERENCE, AND ACCURACY, ARE HEREBY EXCLUDED AND EXPRESSLY DISCLAIMED BY CISCO. CISCO DOES NOT WARRANT THAT THE SAMPLE CODE IS SUITABLE FOR PRODUCTION OR COMMERCIAL USE, WILL OPERATE PROPERLY, IS ACCURATE OR COMPLETE, OR IS WITHOUT ERROR OR DEFECT.

6. GENERAL: This License shall be governed by and interpreted in accordance with the laws of the State of California, excluding its conflict of laws provisions. You agree to comply with all applicable United States export laws, rules, and regulations. If any provision of this License is judged illegal, invalid, or otherwise unenforceable, that provision shall be severed and the rest of the License shall remain in full force and effect. No failure by Cisco to enforce any of its rights related to the Sample Code or to a breach of this License in a particular situation will act as a waiver of such rights. In the event of any inconsistencies with any other terms, this License shall take precedence.