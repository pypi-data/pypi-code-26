#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 04:54:09 2018

@author: ashraya
"""

#import ast
import json
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request

from emulator.InclExcl import generate_device_On_report, generate_exclusion_report, generate_inclusion_report, generate_trigger_report
import emulator.paho.mqtt.publish, emulator.paho.mqtt.subscribe

# App config.
hostname = "localhost"
port = 5000 
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.urandom(12)
app.config['ENV'] = 'development'

def get_devices():
    devices = ['switch', 'alarm', 'light', 'dimmer', 'flood', 'multi', 'door', 'plus']
    return devices

def Log(info):
    if (DEBUG == True):
        filename = "log.log"
        if os.path.exists(filename):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        fp= open(filename, append_write)
        fp.write(info + '\n')
        fp.close()
        app.logger.debug(info)

devices_file = 'selected_devices.json'
devices = []

@app.route("/")
def init():
    return render_template('front.html')
    
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

def get_devices_from_jsonfiles():
    devices = []
    filepath = "emulator/static/prop_files/" 
    Log("get_devices_from_jsonfiles : " + str(filepath))
    if os.path.exists(filepath):
        files = os.listdir(filepath)
        Log("get_devices_from_jsonfiles : " + str(files))
        
        for d in files:
            if (d.find("json") > -1):
                devices.append(d[:d.find('.')])
        Log("get_devices_from_jsonfiles : " + str(devices))
    return devices

def subscribe_to_core_events():
    topics = ["pt:j1/mt:evt/rt:dev/#", "pt:j1/mt:cmd/rt:dev/#"]
    Log("subscribe_to_core_events: " + str(topics))
    emulator.paho.mqtt.subscribe.simple(topics, hostname="localhost")
    #emulator.paho.mqtt.publish.single("pt:j1/mt:cmd/rt:emul/rn:emul/ad:1",
    #        R"""({"serv":"emul","type":"cmd.adapter.get_states","val_t":"null","val":null,"props":null,"tags":null})""")
    Log("subscribe_to_core_events: Done!")
    return

@app.route('/init_onload', methods = ['POST'])
def init_onload():    
    selected_devices = []
    if os.path.exists(devices_file):
        selected_devices = json.load(open(devices_file))
        Log("init_onload : " + str(selected_devices))
        
        subscribe_to_core_events()

    return json.dumps(selected_devices)

@app.route('/init2_onload', methods = ['POST'])
def init2_onload():   
        devices = get_devices_from_jsonfiles()   
        #devices = get_devices()

        Log("init2_onload: " + str(devices))
        return json.dumps(devices)

def update_selected_devices(selected_devices, req, device_id):
    Log("update_selected_devices")
#    dejsonified_prop = json.loads(req)
    dejsonified_prop = req
    Log("update_selected_devices : dejsonified_prop" + str(type(dejsonified_prop)) + ":" + str(dejsonified_prop))
    found = False
    
    if (len(selected_devices) > 0):
        for i in range(len(selected_devices)):
            Log("update_selected_devices : " + str(type(selected_devices[i])))
            Log("update_selected_devices: device_id : " + device_id + " : " + str(type(device_id)))
            Log("update_selected_devices: selected_devices[i].get(\"id\") : " + selected_devices[i]["id"] + " : " + str(type(selected_devices[i].get("id"))))
           
            if (device_id == selected_devices[i].get("id")):
                Log("update_selected_devices: Popping device : " + str(selected_devices[i]))
                selected_devices.pop(i)
                Log("update_selected_devices: Adding device : " + str(type(dejsonified_prop)))
                selected_devices.append(dejsonified_prop)
                found = True
                break

    if ((found == False) or (len(selected_devices) <= 0)):
        selected_devices.append(dejsonified_prop)
            
    Log("update_selected_devices : selected_devices : " + str(selected_devices))
            
    with open(devices_file, 'w+') as jsonfile:
        json.dump(selected_devices, jsonfile)    
        Log('update_selected_devices: Json file updated')
    jsonfile.close()
    
    return

@app.route('/remove_device', methods = ['POST'])
def remove_device():
    data = request.data
    data1 = data
    
    Log("remove_device : " + str(data1))
    
    selected_devices = json.load(open(devices_file))
    Log("remove_device : before : \n" + str(selected_devices))
    
    for device in range(len(selected_devices)):
#        dict_data = ast.literal_eval(selected_devices[device])
        Log("remove_devices: str(selected_devices[device]) : " + str(selected_devices[device]))
        Log("remove_devices: str(selected_devices[device].get(\"id\")) : " + str(selected_devices[device].get("id")))
        
        bdata1 = data1.decode('utf-8')
        ddata1 = selected_devices[device].get("id")
        
        if (str(bdata1) == str(ddata1)):
            Log("remove_device 1: In if condition : " + str(device))
            selected_devices.pop(device)
        
            Log("remove_devices: after : \n" + str(selected_devices))
            
            with open(devices_file, 'w+') as jsonfile:
                json.dump(selected_devices, jsonfile)    
                Log('properties: Json file updated')
            jsonfile.close()
            
            topic, report = generate_exclusion_report(str(bdata1))
            Log("remove_device : topic : "+ topic)
            Log("remove_device : report : "+ str(report))
            
            emulator.paho.mqtt.publish.single(topic, json.dumps(report), hostname=hostname)
            break

    return json.dumps(selected_devices)

@app.route('/get_properties', methods = ['POST'])
def get_properties():
    Log("get_properties")
    if request.method == 'POST':
        data = request.data
        data1 = data

        Log("get_properties : data1 : " + str(data1))
        
        selected_devices = json.load(open(devices_file))
        Log("get_properties : type(selected_devices) : " + str(type(selected_devices)))
        for device in range(len(selected_devices)):
            Log("get_properties : type(selected_devices[i]) : " + str(type(selected_devices[device])))
            bdata1 = data1.decode('utf-8')
            ddata1 = selected_devices[device].get("id")
            Log("get_properties : bdata1 : " + str(bdata1))
            Log("get_properties : ddata1 : " + str(ddata1))
            
            if (str(bdata1) == str(ddata1)):
                return json.dumps(selected_devices[device])
        
    Log("get_properties : Error! ")        
    return "Error"

def update_services(req):
    svs_dict = {}
    for key in req:
        if (key.find("services") > -1):
            key_status = False
            if (req[key] != ""):
                key_status = True
                    
            svs_dict[key[key.find('_')+1:]] = key_status
    
    Log("update_services: services_dict : " + str(svs_dict))
    return svs_dict

@app.route('/properties', methods = ['POST'])
def properties():
    if request.method == 'POST':
        selected_devices = []

        if os.path.exists(devices_file):
            selected_devices = json.load(open(devices_file))

        Log("properties : " + str(selected_devices))
        
        req = request.json
        req1 = json.loads(req)
        Log("properties : req : " + str(req))
        Log("properties : device_id : " + str(req1["id"]))
        device_id = req1["id"]
        Log("properties : device_id : " + str(device_id))
        
        update_selected_devices(selected_devices, req1, device_id)
        
        Log("properties : devices")
        
        modify_svs = update_services(req1)
        devices = get_devices_from_jsonfiles()    
        #devices = get_devices()
        
        device = ""
        for d in devices:
            if (device_id.find(d) > -1):
                device = d
                break
        
        for key in req1:
            if (key.find("services") > -1):
                Log("properties : key : "+ key)
                Log("properties : key[key.find('_')+1] : "+ key[key.find('_')+1:])
                Log("properties : status : " + key + " : " + req1[key])
                topic, report = generate_trigger_report(key[key.find('_')+1:], device_id, device, modify_svs[key[key.find('_')+1:]])
                Log("properties : topic : "+ topic)
                Log("properties : report : "+ str(report))
                emulator.paho.mqtt.publish.single(topic, json.dumps(report), hostname=hostname)
    
    return req

@app.route('/add_device', methods = ['POST'])
def add_device():
    if request.method == 'POST':
        Log("add_device")
        
        selected_devices = []
        if os.path.exists(devices_file):
            selected_devices = json.load(open(devices_file))
        
        req1 = ""
        data = request.data
        data1 = data
        
        Log("add_device: " + str(data1))
        
        data1 = str(data1.decode('utf-8'))
        devices = get_devices_from_jsonfiles()    
        #devices = get_devices()

        for d in devices:
            Log("add_device : devices : "+ d)
            if (data1.find(d) > -1):
                Log("add_device: Device found!")
                file_path = "emulator/static/prop_files/" + d + ".json"
                Log("add_device: " + str(file_path))
                
                if os.path.exists(file_path):
                    Log("add_device: path exists!")
                    req1 = json.load(open(file_path))
                    Log("add_device : req1 : "+ str(req1))
                    
                    Log("test: req[device_id] : " + str(req1["val"]["device_id"]))
                    topic, report = generate_inclusion_report(d, data1, req1["val"])
                    Log("add_device : topic : "+ topic)
                    Log("add_device : report : "+ str(report)+" : " + str(type(report)))
                    report["val"]["device_status"] = "false"
                    req1["val"]["device_status"] = "false"
                    Log("test: req[device_status] : " + str(report["val"]["device_status"]))
                    req1["val"]["id"] = data1
                    update_selected_devices(selected_devices, req1["val"], data1)
                    
                    emulator.paho.mqtt.publish.single(topic, json.dumps(report), hostname=hostname)
                    return json.dumps(report)
                
    return "Error"

@app.route('/toggle_device_status', methods = ['POST'])
def toggle_device_status():
    if request.method == 'POST':
        Log("toggle_device_status")

        data = request.json
        devices = get_devices_from_jsonfiles()    
        #devices = get_devices()

        Log("toggle_device_status: " + str(data))

        # received data : {'toggle_alarm00' : true}
        for d in devices:
            Log("toggle_device_status : devices : "+ d)
            key = list(data)[0]
            if (key.find(d) > -1):
                Log("toggle_device_status: Device found!")
                # device, key, status : switch, switch00, true
                topic, report = generate_device_On_report(d, key[key.find('_')+1:], data[key])
                Log("toggle_device_status : topic : "+ topic)
                Log("toggle_device_status : report : "+ str(report)) 

                # Update in selected_devices.json file
                selected_devices = []
                if os.path.exists(devices_file):
                    selected_devices = json.load(open(devices_file))
                    
                    for d in selected_devices:
                        id = key[key.find('_')+1:]
                        if (id != d["id"]):
                            continue

                        Log("id : " + id + " : d_id : "+d["id"])
                        if "val" in d:
                            d["val"]["device_status"] = data[key]
                            Log("togle_device_status: " + str(d["val"]["device_status"]))
                        else:
                            d["device_status"] = data[key]
                            Log("togle_device_status: " + str(d["device_status"]))

                with open(devices_file, 'w+') as jsonfile:
                    json.dump(selected_devices, jsonfile)    
                    Log('properties: Json file updated')
                jsonfile.close()

                # when the on/off switch is clicked,
                # the basic/default functionality should be 
                # activated/deactivated.

                emulator.paho.mqtt.publish.single(topic, json.dumps(report), hostname=hostname)
                return json.dumps(report)
    return "Error"

def main():
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('log.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    
    app.run(debug=False, port=port)
